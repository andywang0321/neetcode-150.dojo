"""Read the one dojo settings file.

The reviewer owns no configuration format and no key of its own. It reads the engine's
single `settings.toml`: `$DOJO_CONFIG_DIR/settings.toml`, or the engine's default
`$XDG_CONFIG_HOME/dojo/settings.toml` (`~/.config/dojo/settings.toml`) when
`DOJO_CONFIG_DIR` is unset. This module is the only production module that opens a file;
it reads exactly that path and nothing from the engine's database, the curriculum tree,
the assessment modules or the reference solutions.
"""

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SETTINGS_FILENAME = "settings.toml"
DEFAULT_PROVIDER = "deepseek"
CURRICULUM_ID = "neetcode-150"


class ConfigError(Exception):
    """The dojo settings file cannot be read or does not have the expected shape."""


@dataclass(frozen=True, slots=True)
class DojoConfig:
    """The reviewer's slice of the one dojo settings file."""

    provider: str | None = None
    model: str | None = None
    base_url: str | None = None
    reviewer_model: str | None = None


def config_path(env: Mapping[str, str] | None = None) -> Path:
    """Resolve `$DOJO_CONFIG_DIR/settings.toml`, else the engine's XDG default."""
    values = os.environ if env is None else env
    configured = values.get("DOJO_CONFIG_DIR")
    if configured:
        return Path(configured) / SETTINGS_FILENAME
    xdg_config_home = values.get("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"
    return base / "dojo" / SETTINGS_FILENAME


def load_config(path: Path, curriculum: str = CURRICULUM_ID) -> DojoConfig | None:
    """Read the one settings file; a missing file is not a model configuration."""
    if not path.exists():
        return None
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError(f"cannot read {path}: {error}") from error
    try:
        document = tomllib.loads(source)
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML in {path}: {error}") from error
    llm = _table(document, "llm")
    reviewer = _reviewer_table(document, curriculum)
    return DojoConfig(
        provider=_string(llm, "provider", "llm.provider"),
        model=_string(llm, "model", "llm.model"),
        base_url=_string(llm, "base_url", "llm.base_url"),
        reviewer_model=_string(reviewer, "model", f"curricula.{curriculum}.reviewer.model"),
    )


def _reviewer_table(document: Mapping[str, Any], curriculum: str) -> Mapping[str, Any]:
    curricula = _table(document, "curricula")
    if not curricula:
        return {}
    section = curricula.get(curriculum)
    if section is None:
        return {}
    if not isinstance(section, dict):
        raise ConfigError(f"curricula.{curriculum} must be a table")
    reviewer = section.get("reviewer")
    if reviewer is None:
        return {}
    if not isinstance(reviewer, dict):
        raise ConfigError(f"curricula.{curriculum}.reviewer must be a table")
    return reviewer


def _table(document: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    value = document.get(name)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a table")
    return value


def _string(table: Mapping[str, Any], key: str, locator: str) -> str | None:
    value = table.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{locator} must be a non-empty string")
    return value
