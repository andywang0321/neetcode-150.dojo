"""The manifest as a manifest: the engine's loader must accept it.

These tests are the contract gate. The engine's loader checks the shape, the path
rules, the topic graph, the evaluator references and the capability declarations; the
assertions here pin the facts this curriculum claims about itself (18 patterns, 157
items, 155 LeetCode numbers, 5 retired duplicates, six evaluator tools).
"""

from __future__ import annotations

from collections import Counter

import pytest

from tests.conftest import ROOT

TOPICS = 18
ITEMS = 157
NUMBERED = 155
RETIRED = 5
LADDER = 150
CURATED = 7
MEASURED = 127
EXECUTABLE = 30

TOPIC_ORDER = (
    "arrays_and_hashing",
    "two_pointers",
    "sliding_window",
    "stack",
    "binary_search",
    "linked_list",
    "trees",
    "tries",
    "heap",
    "backtracking",
    "graphs",
    "advanced_graphs",
    "dp_1d",
    "dp_2d",
    "greedy",
    "intervals",
    "math_and_geometry",
    "bit_manipulation",
)

RUNGS_PER_TOPIC = {
    "arrays_and_hashing": 9,
    "two_pointers": 5,
    "sliding_window": 6,
    "stack": 7,
    "binary_search": 7,
    "linked_list": 11,
    "trees": 15,
    "tries": 3,
    "heap": 7,
    "backtracking": 9,
    "graphs": 13,
    "advanced_graphs": 6,
    "dp_1d": 12,
    "dp_2d": 11,
    "greedy": 8,
    "intervals": 6,
    "math_and_geometry": 8,
    "bit_manipulation": 7,
}

EVALUATORS = {
    "tests": ("assess.tests", "machine", True),
    "oracle": ("assess.oracle", "machine", False),
    "complexity": ("assess.complexity", "measured", False),
    # Style findings are advisory: the manifest records them as judged evidence, never
    # a machine correctness verdict. The suite's own grade policy agrees.
    "style": ("assess.style", "judged", False),
    "variant": ("variant", "self", False),
    "grade": ("grade", "judged", False),
}

# The evaluator core's own budgets: fast evidence 60 s, the paired measurement 5 min.
TIMEOUTS = {
    "tests": 60,
    "oracle": 60,
    "complexity": 300,
    "style": 60,
    "variant": 60,
    "grade": 60,
}


def _item_keys(item: dict) -> set[str]:
    return set(item)


def test_manifest_has_the_new_shape(manifest: dict) -> None:
    assert set(manifest) == {
        "dojo",
        "display",
        "server",
        "evaluator",
        "topic",
        "item",
        "agents",
        "reflection",
        "capabilities",
        "aliases",
    }
    dojo = manifest["dojo"]
    assert dojo["format"] == 1
    assert dojo["engine"] == ">=0.1,<1"
    assert dojo["id"] == "neetcode-150"
    assert dojo["title"] == "NeetCode 150"
    assert dojo["version"] == "0.1.0"
    assert dojo["license"] == "private"
    assert dojo["source"]
    assert set(dojo["contracts"]) == {"assessment.v1", "review.v1"}

    display = manifest["display"]
    assert display == {
        "topic": "Pattern",
        "item": "Problem",
        "outline": "Roadmap",
        "difficulty": ["Easy", "Medium", "Hard"],
    }

    server = manifest["server"]
    assert server["transport"] == "stdio"
    assert server["command"] == [
        "uv",
        "run",
        "--project",
        ".",
        "python",
        "-m",
        "neetcode_dojo.server",
    ]


def test_old_layout_keys_are_not_carried(manifest: dict) -> None:
    assert "curriculum" not in manifest
    assert "warmup" not in manifest
    assert "language" not in manifest["dojo"]
    assert "interpreter" not in manifest["dojo"]
    for index, item in enumerate(manifest["item"]):
        assert not (
            {"evidence", "artifact", "checks", "assessment", "source", "tags"} & _item_keys(item)
        ), f"item[{index}] carries an old-format key: {sorted(_item_keys(item))}"


def test_topics_are_the_eighteen_patterns(manifest: dict) -> None:
    topics = manifest["topic"]
    assert len(topics) == TOPICS
    assert tuple(topic["id"] for topic in topics) == TOPIC_ORDER
    for index, topic in enumerate(topics):
        assert topic["title"]
        assert topic["summary"]
        expected_prereqs = [] if index == 0 else [TOPIC_ORDER[index - 1]]
        assert topic["prereqs"] == expected_prereqs
        stated = next(int(part) for part in topic["summary"].split() if part.isdigit())
        assert stated == RUNGS_PER_TOPIC[topic["id"]]


def test_items_are_the_157_with_stable_ids(manifest: dict) -> None:
    items = manifest["item"]
    assert len(items) == ITEMS
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids)) == ITEMS

    external = [item["external_id"] for item in items if "external_id" in item]
    assert len(external) == NUMBERED
    assert len(external) == len(set(external))
    assert [item["id"] for item in items if "external_id" not in item] == [
        "generate_sample_to_target_sum",
        "correlation",
    ]

    retired = [item for item in items if item.get("retired")]
    assert len(retired) == RETIRED
    assert all(item.get("external_id") for item in retired)
    assert (
        len([item for item in items if not item.get("retired") and item.get("external_id")])
        == LADDER
    )

    totals = Counter(item["topic"] for item in items)
    assert len(items) == sum(RUNGS_PER_TOPIC.values()) + CURATED
    for topic, rungs in RUNGS_PER_TOPIC.items():
        assert totals[topic] >= rungs

    difficulties = Counter(item["difficulty"] for item in items)
    assert difficulties == Counter({"Medium": 104, "Easy": 32, "Hard": 21})


def test_every_item_declares_a_complete_workspace(manifest: dict) -> None:
    for item in manifest["item"]:
        item_id = item["id"]
        assert item["title"]
        assert item["difficulty"] in manifest["display"]["difficulty"]
        assert item["statement"] == f"content/{item_id}/statement.md"
        assert item["workspace"] == f"content/{item_id}/workspace"
        assert item["check"] == ["python", "check.py"]
        assert item["evaluators"]
        for label in ("statement", "workspace"):
            assert (ROOT / item[label]).exists(), f"{item_id}: missing {label}"


def test_evaluator_declarations_mirror_the_six_tools(manifest: dict) -> None:
    evaluators = manifest["evaluator"]
    assert len(evaluators) == len(EVALUATORS)
    by_id = {evaluator["id"]: evaluator for evaluator in evaluators}
    assert set(by_id) == set(EVALUATORS)
    for evaluator_id, (tool, assurance, required) in EVALUATORS.items():
        evaluator = by_id[evaluator_id]
        assert evaluator["tool"] == tool
        assert evaluator["assurance"] == assurance
        assert evaluator["required"] is required
        assert evaluator["timeout"] == TIMEOUTS[evaluator_id]

    referenced = Counter(reference for item in manifest["item"] for reference in item["evaluators"])
    assert set(referenced) == {"tests", "oracle", "complexity", "style"}
    assert referenced["tests"] == ITEMS
    assert referenced["style"] == ITEMS
    assert referenced["oracle"] == NUMBERED
    assert referenced["complexity"] == MEASURED
    assert referenced["oracle"] + (ITEMS - NUMBERED) == ITEMS


def test_every_evaluator_reference_resolves(manifest: dict) -> None:
    defined = {evaluator["id"] for evaluator in manifest["evaluator"]}
    for item in manifest["item"]:
        assert set(item["evaluators"]) <= defined, item["id"]


def test_capabilities_and_agents(manifest: dict) -> None:
    capabilities = manifest["capabilities"]
    assert set(capabilities) == {"assist", "instruct", "audit", "review", "discuss"}
    for name, prompt in (
        ("assist", "prompts/tutor.md"),
        ("instruct", "prompts/teacher.md"),
        ("audit", "prompts/leak.md"),
        ("discuss", "prompts/discussion.md"),
    ):
        capability = capabilities[name]
        assert capability["impl"] == "llm"
        assert capability["prompt"] == prompt
        assert capability["model"] in {"tutor", "teacher", "auditor", "reviewer"}
        assert (ROOT / prompt).is_file()
    assert capabilities["assist"]["hint_policy"] == "policies/hints.toml"
    assert (ROOT / "policies/hints.toml").is_file()

    review = capabilities["review"]
    assert review == {"impl": "a2a", "agent": "reviewer", "skill": "review"}
    assert manifest["agents"] == {
        "reviewer": {
            "url": "http://127.0.0.1:8766/",
            "command": ["uv", "run", "--project", ".", "python", "-m", "reviewer.server"],
        }
    }

    # Renames are declarations, not implications. The port kept every id stable.
    assert manifest["aliases"] == {"topics": {}, "items": {}}


def test_the_engine_loader_accepts_the_manifest(engine_loader, manifest: dict) -> None:
    curriculum = engine_loader(ROOT)
    assert curriculum.id == manifest["dojo"]["id"]
    assert curriculum.version == manifest["dojo"]["version"]
    assert curriculum.license == "private"
    assert len(curriculum.topics) == TOPICS
    assert len(curriculum.items) == ITEMS
    assert len(curriculum.evaluators) == len(EVALUATORS)
    assert curriculum.server is not None
    assert tuple(curriculum.server.command) == tuple(manifest["server"]["command"])
    assert curriculum.capabilities["review"].impl == "a2a"
    assert curriculum.capabilities["review"].skill == "review"
    assert curriculum.agents["reviewer"].url == "http://127.0.0.1:8766/"
    for item in curriculum.items:
        assert item.statement.is_file(), item.id
        assert item.workspace.is_dir(), item.id
        assert item.check == ("python", "check.py")
        assert item.evaluators


def test_no_duplicate_external_ids_or_item_ids(manifest: dict) -> None:
    ids = [item["id"] for item in manifest["item"]]
    external = [item["external_id"] for item in manifest["item"] if "external_id" in item]
    assert len(ids) == len(set(ids))
    assert len(external) == len(set(external))


@pytest.mark.parametrize("item_id", ["two_sum", "n-queens", "correlation"])
def test_spot_check_statements_are_their_own(manifest: dict, item_id: str) -> None:
    item = next(item for item in manifest["item"] if item["id"] == item_id)
    statement = (ROOT / item["statement"]).read_text(encoding="utf-8")
    assert not statement.startswith(f"{item['title']} [{item['difficulty']}]")
    assert statement.strip()


def test_reflection_questions_cover_time_and_space(manifest: dict) -> None:
    reflection = manifest["reflection"]
    assert [question["id"] for question in reflection] == [
        "time_complexity",
        "space_complexity",
    ]
    assert all(question["prompt"].strip() for question in reflection)
