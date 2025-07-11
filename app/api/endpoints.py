# app/api/endpoints.py

from fastapi import APIRouter, HTTPException

# --- 수정된 부분 ---
from ..schemas import post_schemas
from ..services import post_service 
from app.core import config

router = APIRouter()

@router.post(
    "/generate-curated-post", 
    response_model=post_schemas.EmailSentResponse, 
    tags=["블로그 생성 (고급)"]
)
async def generate_post_endpoint(request: post_schemas.PostRequest):
    """
    AI가 30개 뉴스 중 가장 흥미로운 주제를 직접 선정하고,
    해당 주제로 결과물을 이메일로 발송합니다.
    """
    result = await post_service.create_curated_blog_post(request.section.value)
    
    if "error" in result or not result.get("success"):
        detail = result.get("detail", "알 수 없는 에러가 발생했습니다.")
        if "no_news" in result.values() or "no_match" in result.values():
            raise HTTPException(status_code=404, detail=detail)
        elif "duplicate" in result.values():
            raise HTTPException(status_code=409, detail=detail)
        else:
            raise HTTPException(status_code=500, detail=detail)
            
    return {
        "message": result.get("message"),
        "recipient": config.EMAIL_RECIPIENT_ADDRESS 
    }