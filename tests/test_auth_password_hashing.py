from app.auth.utils import hash_password, verify_password

TEST_PASSWORD = "SyntheticHash!123"


def test_hash_password_does_not_return_raw_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert password_hash != TEST_PASSWORD
    assert password_hash.startswith("$2")


def test_verify_password_accepts_correct_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert verify_password(TEST_PASSWORD, password_hash) is True


def test_verify_password_rejects_wrong_password() -> None:
    password_hash = hash_password(TEST_PASSWORD)

    assert verify_password("WrongSynthetic!123", password_hash) is False
