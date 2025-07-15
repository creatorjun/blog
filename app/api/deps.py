# app/api/deps.py

from fastapi import Depends, HTTPException, status, Request # Request를 다시 추가합니다.
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from ..database import get_db, SessionLocal
from .. import crud, models
from ..core import security
from ..services.naver_service import NaverAPI

oauth2_scheme = HTTPBearer(
    scheme_name="JWT Access Token",
    description="네이버 로그인 후 발급받은 `access_token`을 여기에 붙여넣으세요.",
)

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격 증명을 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_uuid = security.verify_access_token(token=auth.credentials)
        if user_uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.crud_user.get_user_by_uuid(db, user_uuid=user_uuid)
    if user is None:
        raise credentials_exception
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