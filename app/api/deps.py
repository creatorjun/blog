from fastapi import Depends, HTTPException, status
# ⭐️ OAuth2PasswordBearer 대신 HTTPBearer를 사용합니다.
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from .. import models
from ..core import security
from ..database import get_db
from ..crud import crud_user

# ⭐️ 더 간단하고 명확한 HTTPBearer 스키마로 변경합니다.
reusable_oauth2 = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    # ⭐️ 'Authorization: Bearer <TOKEN>' 헤더에서 토큰을 직접 추출합니다.
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> models.User:
    """
    토큰을 검증하고 현재 사용자를 반환하는 의존성입니다.
    """
    token = credentials.credentials
    user_uuid_str = security.verify_token(token)
    if not user_uuid_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # 문자열을 UUID 객체로 변환합니다.
        user_uuid = uuid.UUID(user_uuid_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    # 변환된 UUID로 사용자를 찾습니다.
    user = crud_user.get_user_by_uuid(db, user_uuid=user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return user