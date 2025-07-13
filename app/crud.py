from sqlalchemy.orm import Session
from . import models, schemas

# 특정 ID의 게시글 조회
def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

# 모든 게시글 조회 (페이지네이션 옵션 포함)
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

# 게시글 생성
def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# 게시글 삭제
def delete_post(db: Session, post_id: int):
    # 삭제할 게시글을 조회합니다.
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    # 게시글이 존재하면 삭제하고, 변경사항을 커밋합니다.
    if db_post:
        db.delete(db_post)
        db.commit()

    # 삭제된 객체 정보(또는 없으면 None)를 반환합니다.
    return db_post