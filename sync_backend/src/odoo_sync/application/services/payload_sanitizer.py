from __future__ import annotations

import re

SECRET_PATTERNS = (
    re.compile(r"(password=)[^&\s]+", re.IGNORECASE),
    re.compile(r"(://[^:]+:)[^@]+(@)", re.IGNORECASE),
    re.compile(
        r"((?:password|passwd|pwd|authorization|token)['\"]?\s*[:=]\s*)['\"]?[^,'\"\s]+",
        re.IGNORECASE,
    ),
)


def sanitize_error(value: object) -> str:
    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(
            lambda m: f"{m.group(1)}***{m.group(2) if m.lastindex and m.lastindex > 1 else ''}",
            text,
        )
    return text[:1000]
