# Intelligent Search Bar

This project provides an API for querying financial transactions using natural language. It is built with FastAPI and integrates with OpenAI for summarising query results.

## Setup

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in the required environment variables (database credentials, OpenAI key, etc.).
4. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests

Tests require a PostgreSQL database with sample data and the environment variable `TEST_ID` pointing to a valid account ID. If `TEST_ID` is not set, the tests are skipped.

To execute the test suite:

```bash
pytest
```
