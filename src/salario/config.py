"""Tabulator widget configuration for the Salary Analysis app."""

from typing import Any

_LIKE: dict[str, Any] = {"type": "input", "func": "like", "placeholder": "Filter…"}
_NUM: dict[str, Any] = {"type": "number", "func": ">=", "placeholder": "Min"}

TABULATOR_TITLES: dict[str, str] = {
    "fag": "Field",
    "arbeidssted": "Location",
    "jobbtype": "Job Type",
    "kjønn": "Gender",
    "års utdanning": "Education (yrs)",
    "års erfaring": "Experience (yrs)",
    "lønn": "Salary",
    "inkludert bonus?": "Incl. Bonus?",
    "inkludert provisjon?": "Incl. Commission?",
}

TABULATOR_FORMATTERS: dict[str, Any] = {
    "lønn": {"type": "money", "thousand": " ", "symbol": "", "precision": 0},
}

TABULATOR_HEADER_FILTERS: dict[str, Any] = {
    "fag": _LIKE,
    "arbeidssted": _LIKE,
    "jobbtype": _LIKE,
    "kjønn": _LIKE,
    "års utdanning": _NUM,
    "års erfaring": _NUM,
    "lønn": {**_NUM, "placeholder": "Min salary"},
    "inkludert bonus?": _LIKE,
    "inkludert provisjon?": _LIKE,
}
