# app/schemas/post.py

from pydantic import BaseModel, ConfigDict # 👈 ConfigDict 임포트

# 게시글 생성을 위한 스키마
class PostCreate(BaseModel):
    title: str
    content: str

# 게시글 조회를 위한 스키마 (DB 모델과 연동)
class Post(PostCreate):
    id: int

    # ⭐️ orm_mode = True 를 model_config 설정으로 변경
    model_config = ConfigDict(from_attributes=True)