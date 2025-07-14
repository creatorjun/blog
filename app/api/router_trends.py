from fastapi import APIRouter, Depends
from ..services import naver_trends
from ..schemas import trend as trend_schema
from ..api import deps
from .. import models

router = APIRouter()

@router.get(
    "/{keyword}",
    summary="키워드 검색량 트렌드 조회",
    response_model=trend_schema.TrendResponse,
)
async def get_keyword_trends(
    keyword: str, current_user: models.User = Depends(deps.get_current_user)
):
    """
    지정된 키워드에 대해 최근 일주일간의 일별/연령별 검색량 트렌드를 조회합니다.
    (로그인된 사용자만 사용 가능)
    """
    return await naver_trends.get_combined_trend_data(keyword)