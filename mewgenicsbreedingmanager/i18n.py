import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "zh")

_current_language = DEFAULT_LANGUAGE
_locale_cache: dict[str, dict[str, str]] = {}


def _resolve_locales_dir() -> Path:
    module_dir = Path(__file__).resolve().parent
    candidates = [module_dir / "locales"]

    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", module_dir))
        candidates.append(base / "locales")
        candidates.append(base / "mewgenicsbreedingmanager" / "locales")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


_locales_dir = _resolve_locales_dir()


def _load_locale(language: str) -> dict[str, str]:
    if language in _locale_cache:
        return _locale_cache[language]

    path = _locales_dir / f"{language}.json"
    data: dict[str, str] = {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            for key, value in raw.items():
                if isinstance(key, str) and isinstance(value, str):
                    data[key] = value
    except Exception:
        data = {}

    _locale_cache[language] = data
    return data


def available_languages() -> tuple[str, ...]:
    return SUPPORTED_LANGUAGES


def set_language(language: str) -> str:
    global _current_language
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    _current_language = language
    _load_locale(DEFAULT_LANGUAGE)
    _load_locale(language)
    return _current_language


def get_language() -> str:
    return _current_language


def t(key: str, **kwargs: Any) -> str:
    current = _load_locale(_current_language)
    fallback = _load_locale(DEFAULT_LANGUAGE)

    template = current.get(key) or fallback.get(key) or key
    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except Exception:
        return template
