# app/config.py
from os import getenv

from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    "dbname": getenv("DB_NAME"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "host": getenv("DB_HOST"),
    "port": getenv("DB_PORT")
}

# OpenAI Configuration
OPENAI_API_KEY = getenv("OPENAI_API_KEY")

# FAISS Configuration
EMBEDDING_DIM = 768  # Example embedding size
