from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from .config import (
    SECRET_KEY, 
    ALGORITHM,
    REFRESH_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_MINUTES
)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    주어진 데이터(payload)와 만료 시간을 기반으로 JWT 액세스 토큰을 생성합니다.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 만료 시간이 주어지지 않으면 기본값으로 15분 설정
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str | None:
    """
    JWT 액세스 토큰을 디코딩하여 subject(사용자 UUID)를 반환합니다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if user_uuid is None:
            return None
        return user_uuid
    except JWTError:
        return None

# ⭐️ 아래 두 함수를 추가하세요.
def create_refresh_token(data: dict):
    """
    주어진 데이터(payload)를 기반으로 JWT 리프레시 토큰을 생성합니다.
    """
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> str | None:
    """
    JWT 리프레시 토큰을 디코딩하여 subject(사용자 UUID)를 반환합니다.
    """
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if user_uuid is None:
            return None
        return user_uuid
    except JWTError:
        return None