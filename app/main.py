# app/main.py

import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine
from . import models
from .api.api_router import api_router
# from .core.config import settings # <- 이 줄을 삭제하거나 주석 처리하세요.


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 httpx.AsyncClient 초기화
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield
    # 애플리케이션 종료 시 리소스 정리 (필요 시)


# 개발 환경에서만 사용: DB 테이블 자동 생성
# 프로덕션 환경에서는 Alembic 같은 마이그레이션 도구 사용을 권장합니다.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}