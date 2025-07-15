import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine
from . import models
from .api.api_router import api_router
from .core.exceptions import CustomException
from .core.exception_handlers import custom_exception_handler, unhandled_exception_handler


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

app = FastAPI(
    lifespan=lifespan,
    # 예외 핸들러를 여기에 등록합니다.
    exception_handlers={
        CustomException: custom_exception_handler,
        Exception: unhandled_exception_handler,
    },
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}