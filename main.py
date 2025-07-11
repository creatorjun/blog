# main.py

from fastapi import FastAPI
# 경로를 app.api.endpoints로 수정합니다.
from app.api import endpoints

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="AI 블로그 포스트 생성기 (고급)",
    description="AI가 30개 뉴스 중 가장 흥미로운 주제를 직접 선정하고, 해당 주제로 심층 블로그 포스트를 생성합니다.",
    version="3.0"
)

# app/api/endpoints.py에서 정의한 라우터를 앱에 포함시킵니다.
app.include_router(endpoints.router)

# 루트 경로에 대한 간단한 환영 메시지를 반환합니다.
@app.get("/", tags=["기본"])
def read_root():
    return {"message": "AI 블로그 포스트 생성기 API에 오신 것을 환영합니다. /docs 로 이동하여 API를 테스트해보세요."}