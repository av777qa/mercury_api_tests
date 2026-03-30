# Mercury API — Automated Tests

Automated tests for **Mercury Push Notification API** using `pytest` and `requests`.

## 🚀 Quick Start

```bash
# 1. Setup
git clone <repo_url> && cd mercury_api_tests
pip install -r requirements.txt
cp config/.env.staging .env # Set BASE_URL, TEST_EMAIL, TEST_PASSWORD in .env

# 2. Run Tests
pytest -m smoke -v                  # Run fast smoke tests
pytest -m "not slow" -v             # Run all except slow tests
pytest --html=reports/report.html   # Generate HTML report
```

## 📁 Project Structure

- `clients/`: API clients with JWT authorization.
- `config/`: Environment-based configuration.
- `tests/`: Test suites (Auth, Apps, Campaigns, Segments, etc.).
- `conftest.py`: Root fixtures and setup.

## 🏷 Test Markers

- `smoke`: Critical path validations.
- `happy`: Positive test scenarios.
- `negative`: Error handling and negative cases.
- `slow`: Tests requiring real push dispatch or delays.

## 🔐 CI/CD

Configure these **GitHub Secrets** for the pipeline:
- `STAGING_BASE_URL`
- `TEST_EMAIL`
- `TEST_PASSWORD`

## 📊 Coverage Summary

- **Total Scenarios**: 74
- **Happy Path**: 59
- **Negative Tests**: 15
