# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    .env 파일 또는 환경 변수에서 설정을 로드하며, 정의되지 않은 변수는 허용하지 않습니다.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- 기존 설정 ---
    # Google Gemini API
    GOOGLE_API_KEY: str

    # 네이버 공통 정보
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str

    # 네이버 로그인 API
    NAVER_AUTH_URL: str = "https://nid.naver.com/oauth2.0/authorize"
    NAVER_TOKEN_URL: str = "https://nid.naver.com/oauth2.0/token"
    NAVER_PROFILE_URL: str = "https://openapi.naver.com/v1/nid/me"
    NAVER_CALLBACK_URL: str = "http://localhost:8000/auth/naver/callback"

    # 네이버 데이터랩 API
    NAVER_DATALAB_URL: str = "https://openapi.naver.com/v1/datalab/search"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1일

    # Refresh JWT
    REFRESH_SECRET_KEY: str
    # .env 파일에 정의된 변수명(REFRESH_TOKEN_EXPIRE_DAYS)과 일치시킵니다.
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # --- .env 파일에 있지만 누락되었던 변수들 추가 ---
    PEXELS_API_KEY: str
    UNSPLASH_ACCESS_KEY: str
    EMAIL_SENDER_ADDRESS: str
    EMAIL_SENDER_PASSWORD: str
    EMAIL_RECIPIENT_ADDRESS: str


# 설정 객체 인스턴스 생성
settings = Settings()