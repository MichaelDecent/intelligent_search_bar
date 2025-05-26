# app/config.py
from os import getenv

from dotenv import load_dotenv

load_dotenv()

# FastAPI Configuration
PROJECT_NAME = "MoniMoore AI-Powered Intelligent Search Engine"
VERSION = "1.0.0"
DESCRIPTION = "API for handling user queries and returning financial insights."

API_PREFIX = "/api/v1"

allowed_hosts = getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = allowed_hosts.split(",") if allowed_hosts else []


# Database Configuration
DB_CONFIG = {
    "dbname": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "host": getenv("DB_HOST"),
    "port": getenv("DB_PORT"),
}

# OpenAI Configuration
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
