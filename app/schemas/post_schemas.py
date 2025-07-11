# app/schemas/post_schemas.py

from pydantic import BaseModel, Field
from enum import Enum

class NewsSection(str, Enum):
    """선택 가능한 네이버 뉴스 섹션"""
    politics = "정치"
    economy = "경제"
    society = "사회"
    life_culture = "생활/문화"
    world = "세계"
    it_science = "IT 과학"

class PostRequest(BaseModel):
    """포스트 생성을 요청할 때 사용하는 모델"""
    section: NewsSection = Field(..., description="블로그 포스트를 생성할 뉴스 섹션을 선택하세요.")

class EmailSentResponse(BaseModel):
    """이메일 발송 성공 시의 응답 형식"""
    message: str
    recipient: str