"""The reviewer reads exactly the one dojo settings file, and only its own slice."""

from pathlib import Path

import pytest

from reviewer.config import (
    CURRICULUM_ID,
    DEFAULT_PROVIDER,
    ConfigError,
    DojoConfig,
    config_path,
    load_config,
)


def _write(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "settings.toml"
    path.write_text(source, encoding="utf-8")
    return path


def test_config_path_uses_dojo_config_dir(tmp_path: Path) -> None:
    path = config_path({"DOJO_CONFIG_DIR": str(tmp_path)})

    assert path == tmp_path / "settings.toml"


def test_config_path_falls_back_to_the_engine_xdg_default(tmp_path: Path) -> None:
    path = config_path({"XDG_CONFIG_HOME": str(tmp_path)})

    assert path == tmp_path / "dojo" / "settings.toml"


def test_config_path_falls_back_to_the_home_config_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert config_path({}) == tmp_path / ".config" / "dojo" / "settings.toml"


def test_a_missing_file_is_not_a_configuration(tmp_path: Path) -> None:
    assert load_config(tmp_path / "settings.toml") is None


def test_loads_the_llm_table_and_the_curriculum_reviewer_override(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
[llm]
provider = "openai"
model = "base-model"
base_url = "http://localhost:8000/v1"

[curricula."neetcode-150".reviewer]
model = "review-model"
""",
    )

    assert load_config(path) == DojoConfig(
        provider="openai",
        model="base-model",
        base_url="http://localhost:8000/v1",
        reviewer_model="review-model",
    )


def test_other_curricula_do_not_change_the_reviewer_override(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        f"""
[llm]
model = "base-model"

[curricula."{CURRICULUM_ID}".reviewer]
model = "review-model"

[curricula."other".reviewer]
model = "other-model"
""",
    )

    config = load_config(path)

    assert config is not None
    assert config.reviewer_model == "review-model"


def test_empty_sections_are_defaults(tmp_path: Path) -> None:
    path = _write(tmp_path, "")

    assert load_config(path) == DojoConfig()
    assert DEFAULT_PROVIDER == "deepseek"


def test_reviewer_override_is_optional(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
[llm]
provider = "openai"
model = "base-model"
""",
    )

    config = load_config(path)

    assert config is not None
    assert config.reviewer_model is None


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("[llm\n", "invalid TOML"),
        ('llm = "x"', "llm must be a table"),
        ('[curricula]\n"neetcode-150" = "x"', "must be a table"),
        ('[curricula."neetcode-150"]\nreviewer = "x"', "reviewer must be a table"),
        ("[llm]\nmodel = 3", "llm.model must be a non-empty string"),
        ('[llm]\nmodel = ""', "llm.model must be a non-empty string"),
        ('[llm]\nbase_url = ""', "llm.base_url must be a non-empty string"),
    ],
)
def test_bad_shapes_are_config_errors(tmp_path: Path, source: str, message: str) -> None:
    path = _write(tmp_path, source)

    with pytest.raises(ConfigError, match=message):
        load_config(path)
