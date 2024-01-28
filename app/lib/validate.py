from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional


@dataclass
class Validation:
    ok: bool
    errors: dict[str, list[str]]
    success: dict[Literal["success"], Literal[True]]


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


def validate_form(values: dict[str, Any], checks: dict[str, Check | list[Check]]) -> Validation:
    """
    Validates a form submission

    `values`: The form submission dictionary
    `checks`: The checks to apply for each field in `values`

    Returns a `Validation` object which has `ok` and `response` fields
    `ok` indicates if the form submission was valid
    `response` is the response body to return to the client if not
    """
    from collections import defaultdict

    errors = defaultdict(list)

    for field, value in values.items():
        if field in checks:
            check = checks[field]

            if not isinstance(check, list):
                check = [check]

            for c in check:
                if not c.run(value):
                    errors[field].append(c.message or "Invalid value")

    return Validation(
        ok=len(errors.keys()) == 0,
        errors=dict(errors),
        success={"success": True},
    )
