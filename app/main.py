# app/main.py
from fastapi import FastAPI
from app.api.v1.search import router as search_router

app = FastAPI(
    title="AI-Powered Intelligent Search for Banking",
    description="API for handling user queries and returning financial insights.",
    version="1.0.0"
)

app.include_router(search_router, prefix="/api")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
