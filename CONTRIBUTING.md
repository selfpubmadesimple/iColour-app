# Contributing to PDF to Coloring Book Converter

Thank you for your interest in contributing! This document outlines our development workflow and quality standards.

## 🚀 Pre-Flight Process

**Every feature change must follow this process:**

### 1. Summarize the Request
Before any development, clearly state:
- What feature/change you're implementing
- Why it's needed
- What it will accomplish

**Example:**
> "I'm adding batch PDF processing to allow users to upload multiple PDFs at once and process them sequentially."

### 2. Verify Impact
List all areas that will be affected:
- **Modules to modify**: Which Python files will change
- **New endpoints**: Any new routes or API changes
- **Database changes**: Schema modifications or new models
- **Tests to run**: Which test suites need to pass
- **Dependencies**: New packages or version updates

**Example:**
- Modules: `converter.py`, `models.py`, `templates/convert.html`
- Endpoints: `POST /convert/batch`, `GET /convert/batch-status/<id>`
- Database: New `BatchJob` model
- Tests: `test_converter.py`, `test_api.py`, `test_models.py`
- Dependencies: `celery` for background processing

### 3. Request Approval
Ask for explicit confirmation before proceeding:
> "Please confirm I've captured everything before I proceed."

**Only proceed after receiving ✅ approval.**

## 🧪 Testing Requirements

### Before Any Commit
Run the complete test suite:
```bash
./run_tests.sh
```

This script runs:
- Unit tests with coverage
- Integration tests
- Type checking (MyPy)
- Code formatting (Black)
- Import sorting (isort)
- Linting (Flake8)

### Test Coverage Standards
- **Minimum 80% code coverage**
- **All new functions must have tests**
- **Critical paths require integration tests**

### Writing Tests

#### Unit Tests
```python
# tests/unit/test_utils.py
import pytest
from utils import format_file_size

def test_format_file_size():
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(0) == "0 B"
    assert format_file_size(1048576) == "1.0 MB"
```

#### Integration Tests
```python
# tests/integration/test_api.py
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_registration_flow(client):
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    })
    assert response.status_code == 302  # Redirect after success
```

#### Mocking External APIs
```python
# tests/unit/test_converter.py
import pytest
from unittest.mock import patch, MagicMock
from converter import convert_to_line_art

@patch('converter.client.images.edit')
def test_convert_to_line_art_success(mock_edit):
    # Mock OpenAI API response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url='http://example.com/image.png')]
    mock_edit.return_value = mock_response
    
    # Mock requests.get
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'fake_image_data'
        
        result = convert_to_line_art(b'input_image_data')
        assert result == b'fake_image_data'
```

## 🎯 Code Quality Standards

### Python Style Guide
- **PEP 8 compliance** (enforced by Flake8)
- **Type hints required** for all functions
- **Docstrings required** for public functions
- **Max line length**: 88 characters (Black default)

### Example Function
```python
from typing import Optional, Tuple

def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate a PDF file for processing.
    
    Args:
        file_path: Path to the PDF file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    try:
        import fitz
        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()
        
        if page_count == 0:
            return False, "PDF file is empty"
        if page_count > 20:
            return False, f"PDF has {page_count} pages. Maximum 20 pages allowed."
        
        return True, f"Valid PDF with {page_count} pages"
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"
```

### Database Changes
- **Always use migrations** for schema changes
- **Test migrations both up and down**
- **Include sample data in fixtures**

### Security Requirements
- **Never commit secrets** or API keys
- **Validate all user inputs**
- **Use parameterized queries**
- **Test for common vulnerabilities**

## 🔄 Development Workflow

### 1. Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd pdf-coloring-converter

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run initial tests
./run_tests.sh
```

### 2. Feature Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Follow pre-flight process (see above)

# Develop with TDD approach
# 1. Write failing test
# 2. Implement minimal code to pass
# 3. Refactor and improve
# 4. Repeat

# Run tests frequently
pytest tests/unit/test_your_module.py -v

# Check code quality
./run_tests.sh
```

### 3. Commit Guidelines
```bash
# Format: type(scope): description
git commit -m "feat(converter): add batch PDF processing support"
git commit -m "fix(auth): resolve password validation issue"
git commit -m "test(converter): add integration tests for batch processing"
git commit -m "docs(readme): update API documentation"
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or fixing tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Build process or dependency updates

### 4. Pull Request Process
1. **Run full test suite**: `./run_tests.sh`
2. **Update documentation** if needed
3. **Add/update tests** for new functionality
4. **Create descriptive PR title and description**
5. **Link to relevant issues**
6. **Request review from maintainers**

## 📋 Definition of Done

A feature is considered complete when:

- [ ] **Pre-flight process completed** with approval
- [ ] **All tests pass** (`./run_tests.sh` succeeds)
- [ ] **Code coverage maintained** (≥80%)
- [ ] **Type checking passes** (MyPy clean)
- [ ] **Code formatting applied** (Black, isort)
- [ ] **Documentation updated** (README, docstrings)
- [ ] **Manual testing completed** in development environment
- [ ] **Security review passed** (input validation, no secrets)
- [ ] **Performance impact assessed** (if applicable)
- [ ] **Pull request approved** by maintainer

## 🚨 Emergency Fixes

For critical production issues:

1. **Create hotfix branch** from main: `git checkout -b hotfix/critical-issue`
2. **Implement minimal fix** with test
3. **Skip pre-flight for emergency only**
4. **Fast-track review process**
5. **Deploy immediately after approval**
6. **Follow up with proper feature development**

## 📞 Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or propose ideas
- **Documentation**: Check README and code comments
- **Code Review**: Request feedback on implementation approach

## 🎯 Best Practices Summary

1. **Always follow pre-flight process**
2. **Write tests before implementation**
3. **Keep functions small and focused**
4. **Use type hints consistently**
5. **Mock external dependencies in tests**
6. **Validate all user inputs**
7. **Handle errors gracefully**
8. **Keep commits atomic and descriptive**
9. **Update documentation with changes**
10. **Run full test suite before committing**

Remember: Quality over speed. A well-tested, documented feature is more valuable than a quick implementation that breaks in production.