from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class Validation:
    ok: bool
    response: dict[str, str | bool]


@dataclass
class Check:
    message: Optional[str] = None
    regex: Optional[str] = None
    options: Optional[list] = None
    func: Optional[Callable[[str], bool]] = None

    def run(self, value: str) -> bool:
        if self.regex:
            import re

            regex = re.compile(self.regex)
            return bool(regex.match(value))

        if self.options:
            return value in self.options

        if self.func:
            try:
                return self.func(value)
            except Exception:
                return False

        return True


def validate_form(values: dict[str, Any], checks: dict[str, Check]) -> Validation:
    """
    Validates a form submission

    `values`: The form submission dictionary
    `checks`: The checks to apply for each field in `values`

    Returns a `Validation` object which has `ok` and `response` fields
    `ok` indicates if the form submission was valid
    `response` is the response body to return to the client if not
    """
    errors = {}

    # TODO: Add nice name conversion from field names
    for field, value in values.items():
        if field in checks:
            # TODO: Allow list of checks for one field
            check = checks[field]
            if not check.run(value):
                errors[field] = check.message or "Invalid value"

    return Validation(
        ok=len(errors.keys()) == 0,
        response=errors or {"success": True},
    )
