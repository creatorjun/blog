# app/core/config.py

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# --- API 키 설정 ---

# 구글 Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 네이버 뉴스 API
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 스톡 이미지 API (Pexels, Unsplash)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


# --- 이메일 발송 설정 ---

# 보내는 사람 이메일 주소 (Gmail)
EMAIL_SENDER_ADDRESS = os.getenv("EMAIL_SENDER_ADDRESS")
# 보내는 사람 이메일의 앱 비밀번호
EMAIL_SENDER_PASSWORD = os.getenv("EMAIL_SENDER_PASSWORD")
# 받는 사람 이메일 주소
EMAIL_RECIPIENT_ADDRESS = os.getenv("EMAIL_RECIPIENT_ADDRESS")