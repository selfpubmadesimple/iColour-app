import re

import pytest


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, ""


def validate_username(username):
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 64:
        return False, "Username must be less than 64 characters"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


class TestValidateEmail:

    def test_valid_emails(self):
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "firstname.lastname@company.com",
            "user123@test-domain.com",
        ]
        for email in valid_emails:
            assert validate_email(email) is True, f"Email {email} should be valid"

    def test_invalid_emails(self):
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "",
            "user@.com",
            "user space@example.com",
        ]
        for email in invalid_emails:
            assert validate_email(email) is False, f"Email {email} should be invalid"


class TestValidatePassword:

    def test_valid_passwords(self):
        valid_passwords = ["password123", "MySecret1", "Test1234", "ComplexPassword123"]
        for password in valid_passwords:
            is_valid, message = validate_password(password)
            assert is_valid is True, f"Password {password} should be valid: {message}"

    def test_too_short_password(self):
        for password in ["a1", "test1", "1234567"]:
            is_valid, message = validate_password(password)
            assert is_valid is False
            assert "at least 8 characters long" in message

    def test_no_letters(self):
        for password in ["12345678", "!@#$%^&*"]:
            is_valid, message = validate_password(password)
            assert is_valid is False
            assert "at least one letter" in message

    def test_no_numbers(self):
        for password in ["password", "abcdefgh", "TestPassword"]:
            is_valid, message = validate_password(password)
            assert is_valid is False
            assert "at least one number" in message


class TestValidateUsername:

    def test_valid_usernames(self):
        for username in ["user", "test123", "user_name", "TestUser", "a" * 64]:
            is_valid, message = validate_username(username)
            assert is_valid is True, f"Username {username} should be valid: {message}"

    def test_too_short_username(self):
        for username in ["a", "ab"]:
            is_valid, message = validate_username(username)
            assert is_valid is False
            assert "at least 3 characters long" in message

    def test_too_long_username(self):
        is_valid, message = validate_username("a" * 65)
        assert is_valid is False
        assert "less than 64 characters" in message

    def test_invalid_characters(self):
        for username in ["user-name", "user.name", "user@name", "user name"]:
            is_valid, message = validate_username(username)
            assert is_valid is False
            assert "letters, numbers, and underscores" in message
