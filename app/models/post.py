# app/models/post.py

from sqlalchemy import Column, Integer, String, Text
from ..database import Base  # ⭐️ .database -> ..database 로 변경

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)