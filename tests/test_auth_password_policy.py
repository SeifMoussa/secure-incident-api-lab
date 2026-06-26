import pytest

from app.auth.password_policy import PasswordPolicyError, validate_password_policy

VALID_TEST_PASSWORD = "SyntheticTest!123"


@pytest.mark.parametrize(
    "password",
    [
        "Short1!",
        "synthetictest!123",
        "SyntheticTest!",
        "SyntheticTest123",
        "Password123!",
    ],
)
def test_password_policy_rejects_invalid_passwords(password: str) -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_policy(password)


def test_password_policy_accepts_valid_synthetic_test_password() -> None:
    validate_password_policy(VALID_TEST_PASSWORD)
