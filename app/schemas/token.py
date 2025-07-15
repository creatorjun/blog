from pydantic import BaseModel


class Token(BaseModel):
    """
    JWT 토큰 응답을 위한 Pydantic 모델입니다.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    액세스 토큰 재발급 요청 본문을 위한 Pydantic 모델입니다.
    """
    refresh_token: str


class TokenPayload(BaseModel):
    """
    토큰 페이로드(내용)의 형식을 정의하는 Pydantic 모델입니다.
    """
    sub: str | None = None