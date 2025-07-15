from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from ..database import get_db, SessionLocal
from .. import crud, models
from ..core import security
from ..services.naver_service import NaverAPI
from ..core.exceptions import InvalidTokenError

oauth2_scheme = HTTPBearer(
    scheme_name="JWT Access Token",
    description="네이버 로그인 후 발급받은 `access_token`을 여기에 붙여넣으세요.",
)

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    요청 헤더의 Bearer 토큰을 검증하고 현재 사용자를 반환합니다.
    """
    try:
        user_uuid = security.verify_access_token(token=auth.credentials)
        if user_uuid is None:
            raise InvalidTokenError()
    except JWTError:
        raise InvalidTokenError()

    user = crud.crud_user.get_user_by_uuid(db, user_uuid=user_uuid)
    if user is None:
        # DB에 해당 uuid의 사용자가 없는 경우에도 토큰이 유효하지 않은 것으로 처리
        raise InvalidTokenError()
    return user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_naver_api(request: Request) -> NaverAPI:
    """
    FastAPI의 Request 객체를 통해 app.state에 저장된 공유 http_client를 가져와
    NaverAPI 서비스에 주입합니다. (가장 표준적인 방법입니다.)
    """
    return NaverAPI(client=request.app.state.http_client)