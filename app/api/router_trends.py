# app/api/router_trends.py

from fastapi import APIRouter, Depends

from ..schemas import trend as trend_schema
from ..api import deps
from .. import models
from ..services.naver_service import NaverAPI

router = APIRouter()

@router.get(
    "/{keyword}",
    summary="키워드 검색량 트렌드 조회",
    response_model=trend_schema.TrendResponse,
)
async def get_keyword_trends(
    keyword: str,
    current_user: models.User = Depends(deps.get_current_user),
    naver_api: NaverAPI = Depends(deps.get_naver_api), # 서비스 의존성 주입
):
    """
    지정된 키워드에 대해 최근 일주일간의 일별/연령별 검색량 트렌드를 조회합니다.
    """
    # 서비스 계층의 메서드를 호출하여 비즈니스 로직을 위임합니다.
    return await naver_api.get_combined_trend_data(keyword)