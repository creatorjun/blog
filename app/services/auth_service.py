# app/services/auth_service.py (신규 파일)

from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..core import security
from ..core.config import settings
from .naver_service import NaverAPI

async def handle_naver_login(
    *,
    code: str,
    state: str,
    db: Session,
    naver_api: NaverAPI
) -> schemas.Token:
    """
    네이버 로그인 콜백을 처리하고, 사용자를 생성 또는 조회한 후
    서비스의 JWT 토큰을 발급합니다.
    """
    try:
        # 1. 서비스 계층을 통해 네이버 토큰 및 프로필 정보 요청
        naver_access_token = await naver_api.get_naver_access_token(code, state)
        profile_info = await naver_api.get_naver_user_profile(naver_access_token)

        naver_id = profile_info.get("id")
        if not naver_id:
            raise HTTPException(status_code=400, detail="네이버 사용자 ID를 가져올 수 없습니다.")
        name = profile_info.get("name")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"네이버 인증 실패: {str(e)}")

    # 2. DB에서 사용자 조회 또는 생성
    user = crud.crud_user.get_user_by_naver_id(db, naver_id=naver_id)
    if not user:
        user_in = schemas.UserCreate(name=name, naver_id=naver_id)
        user = crud.crud_user.create_user(db, user_in=user_in)

    # 3. 서비스 자체의 액세스 토큰과 리프레시 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.uuid)}, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(data={"sub": str(user.uuid)})

    return schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

def refresh_user_token(*, refresh_token: str, db: Session) -> schemas.Token:
    """
    리프레시 토큰을 검증하고 새로운 액세스 토큰과 리프레시 토큰을 발급합니다.
    """
    user_uuid = security.verify_refresh_token(refresh_token)
    user = crud.crud_user.get_user_by_uuid(db, user_uuid=user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        data={"sub": str(user.uuid)}, expires_delta=access_token_expires
    )
    new_refresh_token = security.create_refresh_token(data={"sub": str(user.uuid)})

    return schemas.Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )