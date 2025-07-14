from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
import uuid

# 기본 스키마: 공통 필드 정의
class UserBase(BaseModel):
    name: str
    naver_id: str | None = None
    service_start_date: date | None = None
    service_end_date: date | None = None
    is_active_service: bool = False
    payment_method: str | None = None

# 사용자 생성을 위한 스키마
class UserCreate(UserBase):
    pass

# DB에서 사용자 정보를 읽어올 때 (API 응답용) 사용할 스키마
class User(UserBase):
    uuid: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)