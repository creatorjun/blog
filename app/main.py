from fastapi import FastAPI
from .database import engine
from . import models
from .api.api_router import api_router

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My Blog API",
    description="블로그 API 명세서",
    version="0.0.1",
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to my blog API"}