"""The bounded child harnesses used by the assessment quarantine.

They are strings, not importable modules, so the server cannot accidentally import
the assessment code it is about to execute. ``PROBE_HARNESS`` imports the modules and
reports registrations/plans as JSON data; ``RUN_HARNESS`` generates cases, builds
ladder inputs, calls an oracle/reference, or decides one predicate with the
student's module. Both run inside ``proc.run_capped`` with the child-side limits.
"""

from __future__ import annotations

PROBE_HARNESS = r"""
import importlib.util, json, os, random, sys

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _emit(payload):
    try:
        blob = json.dumps(payload)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        blob = json.dumps({"fatal": f"the probe produced non-JSON data: {detail}"})
    os.write(1, blob.encode("utf-8", "replace"))

def _main():
    try:
        from neetcode_dojo.proc import apply_child_limits
        apply_child_limits()
    except Exception:
        pass
    try:
        from neetcode_dojo import registry
    except Exception as exc:
        _emit({"fatal": f"the registry is not importable: {exc}"})
        return
    paths = json.loads(sys.argv[1])
    out = {}
    for index, path in enumerate(paths):
        registry.reset()
        report = {"registrations": {}, "functions": {}, "plans": {}, "rubrics": {},
                  "case_samples": {}, "error": None}
        try:
            _load(path, f"neetcode_dojo_assessment_probe_{index}")
            report["registrations"] = registry.registrations()
            # The Python names behind the registrations: a harness that imports the
            # module and calls a *function* needs the name, and the registration
            # name is the item id, which need not be the function's own name.
            report["functions"] = {
                kind: {name: getattr(fn, "__name__", name) for name, fn in store.items()}
                for kind, store in registry.STORES.items()
            }
            for item_id, plan_fn in registry.MEASURES.items():
                try:
                    plan = plan_fn({})
                    json.dumps(plan)  # a plan must be data, not a live object
                    report["plans"][item_id] = plan
                except Exception as exc:
                    report["error"] = (report["error"] or "") + (
                        f"the plan for {item_id!r} is not data: "
                        f"{type(exc).__name__}: {exc}; "
                    )
            for item_id, rubric_fn in registry.RUBRICS.items():
                try:
                    rubric = rubric_fn()
                    json.dumps(rubric)
                    report["rubrics"][item_id] = rubric
                except Exception as exc:
                    report["error"] = (report["error"] or "") + (
                        f"the rubric for {item_id!r} is not data: "
                        f"{type(exc).__name__}: {exc}; "
                    )
            for item_id, cases_fn in registry.CASES.items():
                sample = {"sizes": [], "tags": [], "predicates": [],
                          "decidable": True, "error": None}
                for n in (2, 7):
                    try:
                        produced = cases_fn(n, random.Random(f"neetcode-dojo-probe-{n}"))
                        if not isinstance(produced, (list, tuple)) or not produced:
                            sample["error"] = (
                                "the generator did not return a case (expected "
                                "(args, expected[, extras]))"
                            )
                            sample["decidable"] = False
                            continue
                        extras = (
                            produced[2]
                            if len(produced) > 2 and isinstance(produced[2], dict)
                            else {}
                        )
                        sample["sizes"].append(n)
                        sample["tags"].extend(
                            sorted(k for k in extras if k in ("compare", "predicate", "ops"))
                        )
                        if extras.get("predicate"):
                            sample["predicates"].append(str(extras["predicate"]))
                        decided = (
                            len(produced) >= 2
                            or "predicate" in extras
                            or "ops" in extras
                        )
                        sample["decidable"] = sample["decidable"] and decided
                    except Exception as exc:
                        sample["error"] = f"{type(exc).__name__}: {exc}"
                        sample["decidable"] = False
                report["case_samples"][item_id] = sample
        except BaseException as exc:
            report["error"] = f"{type(exc).__name__}: {exc}"
        out[path] = report
    _emit(out)

_main()
"""

#: The child harness that *runs* a curriculum's assessment code: generate cases at
#: given sizes, build ladder inputs, call an oracle/reference, or decide a predicate
#: with the student's module. One child per request, bounded like every other
#: subprocess here.

RUN_HARNESS = r"""
import copy, importlib.util, json, os, random, sys

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _emit(payload):
    try:
        blob = json.dumps(payload)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        blob = json.dumps({"ok": False, "error": f"the run produced non-JSON data: {detail}"})
    os.write(1, blob.encode("utf-8", "replace"))

def _main():
    request = json.loads(sys.argv[1])
    try:
        from neetcode_dojo.proc import apply_child_limits
        apply_child_limits()
    except Exception:
        pass
    out = {"ok": False}
    try:
        from neetcode_dojo import registry
        registry.reset()
        _load(request["module"], "neetcode_dojo_assessment_run")
        kind = request["kind"]
        item = request["item"]
        if kind == "cases":
            generate = registry.CASES[item]
            produced = []
            for spec in request["requests"]:
                result = generate(spec["n"], random.Random(spec["seed"]))
                args, expected = result[0], result[1]
                extras = result[2] if len(result) > 2 and isinstance(result[2], dict) else {}
                produced.append({"args": args, "expected": expected, **extras})
            out = {"ok": True, "cases": produced}
        elif kind == "inputs":
            out = {
                "ok": True,
                "args": registry.INPUTS[item](request["n"], random.Random(request["seed"])),
            }
        elif kind == "inputs_many":
            build = registry.INPUTS[item]
            out = {
                "ok": True,
                "inputs": [
                    build(spec["n"], random.Random(spec["seed"]))
                    for spec in request["requests"]
                ],
            }
        elif kind in ("oracle", "reference"):
            store = registry.ORACLES if kind == "oracle" else registry.REFERENCES
            # `args` comes back as the call *left* it: an in-place solution
            # ("compare": "mutates") returns None and its whole contract is the
            # effect on the arguments, so the caller needs both.
            call_args = request["args"]
            out = {"ok": True, "value": store[item](*call_args), "mutated_args": call_args}
        elif kind == "oracle_many":
            call = registry.ORACLES[item]
            values = []
            for entry in request["calls"]:
                try:
                    call_args = copy.deepcopy(entry.get("args", []))
                    if entry.get("ops") is not None:
                        value = call(entry["ops"])
                    else:
                        value = call(*call_args)
                    values.append({"ok": True, "value": value, "mutated_args": call_args})
                except BaseException as exc:
                    values.append({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
            out = {"ok": True, "values": values}
        elif kind == "checker":
            # The student's module is loaded first (it is the untrusted side), then
            # the checker is called with it. This mirrors the old harness's
            # (module, got, args) signature, but in the assessment child rather than
            # in the server's process.
            solution = _load(request["code_file"], "neetcode_dojo_solution")
            checker = registry.CHECKERS[request["checker"]]
            out = {
                "ok": True,
                "passed": bool(checker(solution, request["got"], request["args"])),
            }
        elif kind == "rubric":
            out = {"ok": True, "value": registry.RUBRICS[item]()}
        else:
            out = {"ok": False, "error": f"cannot run {kind!r}"}
    except BaseException as exc:
        out = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    _emit(out)

_main()
"""
