from sqlalchemy.orm import Session
import uuid
from .. import models, schemas

def get_user_by_uuid(db: Session, *, user_uuid: uuid.UUID):
    """
    UUID로 사용자를 조회합니다.
    """
    return db.query(models.User).filter(models.User.uuid == str(user_uuid)).first()


def get_user_by_naver_id(db: Session, *, naver_id: str):
    """
    네이버 ID로 사용자를 조회합니다.
    """
    return db.query(models.User).filter(models.User.naver_id == naver_id).first()


def create_user(db: Session, *, user_in: schemas.UserCreate):
    """
    새로운 사용자를 생성합니다.
    """
    db_user = models.User(
        name=user_in.name,
        naver_id=user_in.naver_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user