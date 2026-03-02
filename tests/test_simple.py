"""
Simple standalone tests that don't require the full application.
"""

import os
import tempfile


def test_python_environment():
    """Test that Python environment is working."""
    assert True
    print("✓ Python environment is working")


def run_test(test_func):
    """Simple test runner."""
    try:
        test_func()
        print(f"✓ {test_func.__name__} passed")
        return True
    except Exception as e:
        print(f"✗ {test_func.__name__} failed: {e}")
        return False


def test_file_operations():
    """Test basic file operations."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        temp_path = f.name

    try:
        assert os.path.exists(temp_path)
        with open(temp_path, "r") as f:
            content = f.read()
        assert content == "test content"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_import_basic_modules():
    """Test that basic modules can be imported."""
    import json
    import re
    import time

    # Test basic functionality
    data = {"test": "value"}
    json_str = json.dumps(data)
    assert json.loads(json_str) == data

    pattern = r"\d+"
    assert re.match(pattern, "123")

    start_time = time.time()
    assert isinstance(start_time, float)


def test_werkzeug_import():
    """Test that Werkzeug security functions work."""
    from werkzeug.security import check_password_hash, generate_password_hash

    password = "testpassword123"
    hash_value = generate_password_hash(password)
    assert hash_value != password
    assert check_password_hash(hash_value, password)
    assert not check_password_hash(hash_value, "wrongpassword")


def test_email_validation():
    """Test email validation logic."""
    import re

    def validate_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    # Valid emails
    assert validate_email("user@example.com")
    assert validate_email("test.email@domain.org")
    assert validate_email("user123@test-domain.com")

    # Invalid emails
    assert not validate_email("invalid-email")
    assert not validate_email("user@")
    assert not validate_email("@domain.com")
    assert not validate_email("")


def test_password_validation():
    """Test password validation logic."""
    import re

    def validate_password(password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[a-zA-Z]", password):
            return False, "Password must contain at least one letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        return True, ""

    # Valid passwords
    assert validate_password("password123")[0]
    assert validate_password("Test1234")[0]

    # Invalid passwords
    assert not validate_password("short1")[0]
    assert not validate_password("12345678")[0]
    assert not validate_password("onlyletters")[0]


def test_file_size_formatting():
    """Test file size formatting."""

    def format_file_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024.0 and unit_index < len(size_units) - 1:
            size /= 1024.0
            unit_index += 1

        return f"{size:.1f} {size_units[unit_index]}"

    assert format_file_size(0) == "0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"


if __name__ == "__main__":
    """Run all tests when script is executed directly."""
    print("🧪 Running simple tests...")

    tests = [
        test_python_environment,
        test_file_operations,
        test_import_basic_modules,
        test_werkzeug_import,
        test_email_validation,
        test_password_validation,
        test_file_size_formatting,
    ]

    passed = 0
    failed = 0

    for test in tests:
        if run_test(test):
            passed += 1
        else:
            failed += 1

    print(f"\n📊 Test Results: {passed} passed, {failed} failed")

    if failed > 0:
        exit(1)
    else:
        print("✅ All tests passed!")
        exit(0)
