from fastapi import APIRouter
from . import router_auth, router_trends

api_router = APIRouter()

# 인증 관련 엔드포인트들을 포함
api_router.include_router(router_auth.router, prefix="/auth", tags=["auth"])

# 트렌드 관련 엔드포인트들을 포함
api_router.include_router(router_trends.router, prefix="/trends", tags=["trends"])

# 제미나이 관련 엔드포인트들을 포함
# api_router.include_router(router_gemini.router, tags=["gemini"])