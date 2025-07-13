# app/api/router_posts.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Post)
def create_new_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """
    새로운 게시글을 생성합니다.
    """
    return crud.create_post(db=db, post=post)


@router.get("/", response_model=List[schemas.Post])
def read_all_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    모든 게시글을 조회합니다.
    """
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts


@router.get("/{post_id}", response_model=schemas.Post)
def read_single_post(post_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 게시글을 조회합니다.
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_post(post_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 게시글을 삭제합니다.
    """
    # crud 함수를 호출하여 게시글을 삭제합니다.
    deleted_post = crud.delete_post(db=db, post_id=post_id)

    # 만약 삭제하려는 게시글이 DB에 없다면 404 에러를 발생시킵니다.
    if deleted_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # 성공적으로 삭제되면, 내용 없이 204 상태 코드를 반환합니다.
    return Response(status_code=status.HTTP_204_NO_CONTENT)