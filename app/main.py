from fastapi import FastAPI

from app.api.v1.search import router as search_router

app = FastAPI(
    title="MoniMoore AI-Powered Intelligent Search Engine",
    description="API for handling user queries and returning financial insights.",
    version="1.0.0",
)

app.include_router(search_router, prefix="/api")
