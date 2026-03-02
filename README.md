# PDF to Coloring Book Converter

Transform your full-color PDF illustrations into beautiful coloring books using advanced AI technology.

## ✨ Features

- **AI-Powered Conversion**: Uses OpenAI's image editing API to convert colorful illustrations into clean line art
- **User Authentication**: Secure registration and login system with activity tracking
- **Multiple Output Formats**: Get both individual PNG files and a complete PDF coloring book
- **Processing History**: Dashboard shows conversion statistics and download history
- **Professional Interface**: Modern dark theme with responsive design

## 🚀 Pre-Flight Feature Checklist

Whenever you're about to add or change functionality:

1. **Summarize**
   > "I'm adding `<feature>` to do `<X, Y, Z>`."

2. **Verify Impact**
   - I will run `pytest` on these modules: `converter`, `auth`, `models`, `utils`
   - I will re-run `run_tests.sh` to ensure no regressions
   - I will check these endpoints: `/convert`, `/auth/login`, `/auth/register`, `/dashboard`

3. **Ask for Approval**
   > "Please confirm I've captured everything before I proceed."

_Only after step 3 and your "✅ go‑ahead" should development begin._

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- OpenAI API key

### Installation

1. **Clone and install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
export SESSION_SECRET="your-secret-key"
```

3. **Run the application:**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## 🧪 Testing

### Run All Tests
```bash
./run_tests.sh
```

### Individual Test Commands
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=. --cov-report=html

# Type checking
mypy .

# Code formatting
black . --check
isort . --check-only

# Linting
flake8 .
```

### Test Structure
```
tests/
├── fixtures/
│   ├── sample.pdf          # Test PDF file
│   └── sample_image.png    # Test image
├── unit/
│   ├── test_auth.py        # Authentication tests
│   ├── test_converter.py   # PDF conversion tests
│   ├── test_models.py      # Database model tests
│   └── test_utils.py       # Utility function tests
└── integration/
    ├── test_api.py         # API endpoint tests
    └── test_workflow.py    # End-to-end workflow tests
```

## 📁 Project Structure

```
.
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── auth.py             # Authentication routes and logic
├── converter.py        # PDF conversion functionality
├── models.py           # Database models
├── utils.py            # Utility functions
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JavaScript, images
├── tests/              # Test suite
└── uploads/            # Temporary file storage
```

## 🔧 Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/new-feature`
2. **Follow Pre-Flight Process**: Use checklist above
3. **Write Tests First**: Add tests before implementation
4. **Run Quality Checks**: `./run_tests.sh`
5. **Submit for Review**: Create pull request

## 📊 Key Components

### Authentication System
- User registration with validation
- Secure password hashing
- Session management with Flask-Login
- Activity tracking and user statistics

### PDF Conversion Engine
- File upload with security validation
- PDF page extraction using PyMuPDF
- AI-powered line art conversion via OpenAI
- Multi-format output generation (PNG + PDF)
- Automatic file cleanup

### Database Models
- User management with relationships
- Activity logging with processing metrics
- PostgreSQL with SQLAlchemy ORM

## 🔒 Security Features

- Secure filename handling
- File type and size validation
- Password strength requirements
- Session management
- Input sanitization

## 📈 Performance Considerations

- File size limits (50MB max)
- Page count limits (20 pages max)
- Automatic cleanup of old files
- Database connection pooling
- Processing time tracking

## 🎨 UI/UX Features

- Bootstrap 5 dark theme
- Responsive design
- Progress indicators
- File drag-and-drop
- Real-time validation
- Accessibility features

## 🚀 Deployment

The application is configured for easy deployment on Replit:
- Environment variable support
- PostgreSQL integration
- Gunicorn WSGI server
- Proxy-friendly configuration

## 📝 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - User profile

### Conversion Endpoints
- `GET /convert/dashboard` - User dashboard
- `POST /convert/` - PDF conversion
- `GET /convert/download/<id>` - Download previous conversion

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📄 License

This project is built for educational and personal use.