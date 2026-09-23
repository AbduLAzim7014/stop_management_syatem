from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, add_member_columns, engine
from app.routes import router

settings = get_settings()
Base.metadata.create_all(bind=engine)
add_member_columns()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.[0-9]+\.[0-9]+):5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs", "api": "/api"}
