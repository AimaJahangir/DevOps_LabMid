"""Validation rules for assignment submissions."""
from urllib.parse import urlparse

REQUIRED = {
    "name": "Student name is required.",
    "reg_no": "Registration number is required.",
    "title": "Assignment title is required.",
    "url": "Submission URL is required.",
}


def is_valid_url(value: str) -> bool:
    try:
        p = urlparse(value)
    except ValueError:
        return False
    return p.scheme in ("http", "https") and bool(p.netloc) and "." in p.netloc and " " not in value


def validate(data: dict) -> dict:
    """Return {field: message}. Empty dict means valid."""
    errors = {}
    for field, msg in REQUIRED.items():
        if not str(data.get(field, "")).strip():
            errors[field] = msg
    url = str(data.get("url", "")).strip()
    if url and not is_valid_url(url):
        errors["url"] = "Submission URL is invalid. Use a full link such as https://github.com/user/repo."
    return errors
