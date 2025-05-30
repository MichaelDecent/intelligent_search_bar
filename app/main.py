from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.search import router as search_router
from app import config


def get_application():
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION, description=config.DESCRIPTION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(search_router, prefix="/api/v1")

    return app


app = get_application()
