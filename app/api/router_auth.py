from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from ..core.config import settings
from ..database import get_db
from ..schemas import token as token_schema, user as user_schema
from ..api import deps
from .. import models
from ..services.naver_service import NaverAPI
from ..services import auth_service # 새로 추가될 인증 서비스

router = APIRouter()


@router.get("/naver", summary="네이버 로그인 URL 반환")
def naver_login(state: str = "your_random_state_string"):
    """
    사용자를 네이버 인증 페이지로 리디렉션하기 위한 URL을 생성하여 반환합니다.
    """
    return {
        "url": f"{settings.NAVER_AUTH_URL}?response_type=code&client_id={settings.NAVER_CLIENT_ID}&redirect_uri={settings.NAVER_CALLBACK_URL}&state={state}"
    }


@router.get(
    "/naver/callback",
    summary="네이버 로그인 콜백 처리 및 JWT 발급",
    response_model=token_schema.Token,
)
async def naver_login_callback(
    code: str = Query(...),
    state: str = Query(..., description="CSRF 방지를 위한 상태 토큰"),
    db: Session = Depends(get_db),
    naver_api: NaverAPI = Depends(deps.get_naver_api),
):
    """
    네이버 로그인 성공 후 리디렉션되는 콜백 엔드포인트입니다.
    네이버로부터 받은 인증 코드로 사용자 프로필을 조회하고,
    시스템에 등록된 사용자가 아니면 새로 생성합니다.
    이후 서비스의 액세스 토큰과 리프레시 토큰을 발급합니다.
    """
    # 인증 로직을 서비스 계층으로 위임합니다.
    return await auth_service.handle_naver_login(code=code, state=state, db=db, naver_api=naver_api)


@router.post(
    "/refresh",
    summary="액세스 토큰 재발급",
    response_model=token_schema.Token,
)
def refresh_token(
    body: token_schema.RefreshTokenRequest = Body(...), # embed=True 제거, Body에서 직접 모델을 받음
    db: Session = Depends(get_db),
):
    """
    유효한 리프레시 토큰으로 새로운 액세스 토큰과 리프레시 토큰을 발급합니다.
    """
    # 토큰 재발급 로직을 서비스 계층으로 위임합니다.
    return auth_service.refresh_user_token(refresh_token=body.refresh_token, db=db)


@router.post("/logout", summary="로그아웃")
def logout(current_user: models.User = Depends(deps.get_current_user)):
    """
    로그아웃을 처리합니다. 클라이언트 측에서 토큰을 삭제해야 합니다.
    """
    # 실제 구현에서는 토큰을 블랙리스트에 추가하는 로직이 포함될 수 있습니다.
    return {"message": "성공적으로 로그아웃되었습니다."}


@router.get(
    "/me",
    summary="현재 로그인된 사용자 정보 조회",
    response_model=user_schema.User,
)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    """
    현재 인증된 사용자의 정보를 반환합니다.
    """
    return current_user