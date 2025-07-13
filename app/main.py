from fastapi import FastAPI
from .database import engine
from . import models
from .api import router_posts

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My Blog API",
    description="블로그 API 명세서",
    version="0.0.1",
)

# '/posts' 경로로 들어오는 모든 요청을 router_posts.router로 전달
app.include_router(router_posts.router, prefix="/posts", tags=["posts"])

@app.get("/")
def read_root():
    return {"message": "Welcome to my blog API"}