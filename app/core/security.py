from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# 비밀번호 해싱을 위한 CryptContext 인스턴스 생성
# bcrypt는 안전한 해싱 알고리즘으로 널리 사용됩니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    액세스 토큰을 생성합니다.

    Args:
        data (dict): 토큰의 페이로드(payload)에 포함될 데이터.
        expires_delta (timedelta | None, optional): 토큰의 만료 시간.
            None이면 설정 파일의 기본값을 사용합니다.

    Returns:
        str: 생성된 JWT 액세스 토큰.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> str:
    """
    액세스 토큰을 검증하고 사용자 식별자(UUID)를 반환합니다.

    Args:
        token (str): 검증할 JWT 토큰.

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우.

    Returns:
        str: 토큰에서 추출한 사용자 UUID.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_uuid: str | None = payload.get("sub")
        if user_uuid is None:
            raise JWTError("User UUID not found in token payload.")
        return user_uuid
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="자격 증명이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    리프레시 토큰을 생성합니다.

    Args:
        data (dict): 토큰의 페이로드(payload)에 포함될 데이터.
        expires_delta (timedelta | None, optional): 토큰의 만료 시간.
            None이면 설정 파일의 기본값을 사용합니다.

    Returns:
        str: 생성된 JWT 리프레시 토큰.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_refresh_token(token: str) -> str:
    """
    리프레시 토큰을 검증하고 사용자 식별자(UUID)를 반환합니다.

    Args:
        token (str): 검증할 JWT 리프레시 토큰.

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우.

    Returns:
        str: 토큰에서 추출한 사용자 UUID.
    """
    try:
        payload = jwt.decode(
            token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_uuid: str | None = payload.get("sub")
        if user_uuid is None:
            raise JWTError("User UUID not found in token payload.")
        return user_uuid
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 비밀번호와 해시된 비밀번호가 일치하는지 확인합니다.

    Args:
        plain_password (str): 사용자가 입력한 비밀번호.
        hashed_password (str): 데이터베이스에 저장된 해시된 비밀번호.

    Returns:
        bool: 비밀번호 일치 여부.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시하여 반환합니다.

    Args:
        password (str): 해시할 비밀번호.

    Returns:
        str: 해시된 비밀번호 문자열.
    """
    return pwd_context.hash(password)

def verify_access_token(token: str) -> Optional[str]:
    """
    주어진 JWT 액세스 토큰을 검증하고, 유효하다면 사용자 UUID를 반환합니다.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # 토큰에서 'sub' (subject) 클레임을 추출합니다.
        user_uuid: Optional[str] = payload.get("sub")
        if user_uuid is None:
            return None
        return user_uuid
    except JWTError:
        # 토큰이 유효하지 않은 경우 (만료, 서명 오류 등)
        return None