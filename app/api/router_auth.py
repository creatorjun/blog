import httpx
import secrets
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.config import (
    NAVER_CLIENT_ID,
    NAVER_CLIENT_SECRET,
    NAVER_CALLBACK_URL,
    NAVER_AUTH_URL,
    NAVER_TOKEN_URL,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..core import security
from ..database import get_db
from ..crud import crud_user
from ..schemas import user as user_schema, token as token_schema
from ..api import deps
from .. import models

router = APIRouter()


@router.get("/naver", summary="네이버 로그인 페이지로 리디렉션")
def naver_login():
    """
    사용자를 네이버 로그인 및 동의 화면으로 보냅니다.
    """
    state = secrets.token_urlsafe(16)
    redirect_url = (
        f"{NAVER_AUTH_URL}?response_type=code"
        f"&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={NAVER_CALLBACK_URL}"
        f"&state={state}"
    )
    return RedirectResponse(url=redirect_url)


@router.get(
    "/naver/callback",
    summary="네이버 로그인 콜백 처리 및 JWT 발급",
    response_model=token_schema.Token,
)
async def naver_login_callback(
    code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)
):
    """
    네이버 로그인 성공 후, 서비스의 액세스 토큰과 리프레시 토큰을 발급합니다.
    """
    # 1. 액세스 토큰 요청
    token_params = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    async with httpx.AsyncClient() as client:
        token_res = await client.get(NAVER_TOKEN_URL, params=token_params)
        token_data = token_res.json()
    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Naver token error: {token_data['error_description']}",
        )
    access_token = token_data.get("access_token")

    # 2. 사용자 프로필 정보 요청
    profile_url = "https://openapi.naver.com/v1/nid/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        profile_res = await client.get(profile_url, headers=headers)
        profile_data = profile_res.json()
    if profile_data.get("resultcode") != "00":
        raise HTTPException(
            status_code=500, detail="Failed to get user profile from Naver."
        )
    naver_account_info = profile_data.get("response")
    naver_id = naver_account_info.get("id")
    name = naver_account_info.get("name")

    # 3. DB에서 사용자 조회 또는 생성
    db_user = crud_user.get_user_by_naver_id(db, naver_id=naver_id)
    if not db_user:
        user_in = user_schema.UserCreate(name=name, naver_id=naver_id)
        db_user = crud_user.create_user(db, user_in=user_in)

    # 4. 액세스 토큰과 리프레시 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": str(db_user.uuid)}, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(data={"sub": str(db_user.uuid)}),
    }


@router.post("/refresh", summary="액세스 토큰 갱신", response_model=token_schema.Token)
def refresh_token(
    refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)
):
    """
    유효한 리프레시 토큰으로 새로운 액세스 토큰과 리프레시 토큰을 발급합니다.
    """
    user_uuid_str = security.verify_refresh_token(refresh_token)
    if not user_uuid_str:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        user_uuid = uuid.UUID(user_uuid_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = crud_user.get_user_by_uuid(db, user_uuid=user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": str(user.uuid)}, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(data={"sub": str(user.uuid)}),
    }


@router.post("/logout", summary="로그아웃")
def logout(current_user: models.User = Depends(deps.get_current_user)):
    """
    사용자 로그아웃 처리.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", summary="현재 사용자 정보 확인", response_model=user_schema.User)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    """
    현재 로그인된 사용자의 정보를 반환합니다.
    """
    return current_user