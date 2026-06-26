"""Password policy validation for synthetic lab users."""

from functools import lru_cache
from pathlib import Path

MIN_PASSWORD_LENGTH = 12
SPECIAL_CHARACTERS = set("!@#$%^&*()-_=+[]{};:,.?/|`~")


class PasswordPolicyError(ValueError):
    """Raised when a password fails the registration policy."""


@lru_cache
def load_common_passwords() -> frozenset[str]:
    """Load a small static denylist of unsafe common passwords."""
    denylist_path = Path(__file__).with_name("common_passwords.txt")
    return frozenset(
        line.strip().lower()
        for line in denylist_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def validate_password_policy(password: str) -> None:
    """Validate a registration password without returning the password value."""
    if len(password) < MIN_PASSWORD_LENGTH:
        msg = "Password must be at least 12 characters long."
        raise PasswordPolicyError(msg)
    if not any(character.isupper() for character in password):
        msg = "Password must include at least one uppercase letter."
        raise PasswordPolicyError(msg)
    if not any(character.isdigit() for character in password):
        msg = "Password must include at least one digit."
        raise PasswordPolicyError(msg)
    if not any(character in SPECIAL_CHARACTERS for character in password):
        msg = "Password must include at least one special character."
        raise PasswordPolicyError(msg)
    if password.lower() in load_common_passwords():
        msg = "Password is too common."
        raise PasswordPolicyError(msg)
