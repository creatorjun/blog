import uuid
from sqlalchemy import Column, String, Date, Boolean, DateTime, func
from sqlalchemy.dialects.mysql import CHAR
from ..database import Base

class User(Base):
    __tablename__ = "users"

    # 1. 서버 자체 식별자 (UUID)
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 2. 네이버로부터 받은 식별자 (Naver Login ID)
    naver_id = Column(String(255), unique=True, index=True, nullable=True)

    # 3. 회원 이름
    name = Column(String(50), nullable=False)

    # 4. 가입일
    created_at = Column(DateTime, server_default=func.now())

    # 5. 서비스 시작일
    service_start_date = Column(Date, nullable=True)

    # 6. 서비스 종료일
    service_end_date = Column(Date, nullable=True)

    # 7. 서비스 가입 여부
    is_active_service = Column(Boolean, default=False, nullable=False)

    # 8. 결제 방식
    payment_method = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<User(name='{self.name}', naver_id='{self.naver_id}')>"