import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 네이버 로그인 API 정보
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_CALLBACK_URL = "http://localhost:8000/auth/naver/callback"

# 네이버 데이터랩 API 정보
NAVER_DATALAB_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_DATALAB_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1일

# Refresh JWT
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14  # 14일