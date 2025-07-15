# app/services/naver_service.py

import httpx
import json
import logging
import asyncio
from datetime import date, timedelta
from typing import List, Dict, Any

from ..core.config import settings
from ..schemas import trend as trend_schema

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 네이버 API에서 사용하는 연령대 코드
AGE_GROUPS = {
    "10s": ["2", "3"], "20s": ["4", "5"], "30s": ["6", "7"],
    "40s": ["8", "9"], "50s": ["10"], "60s+": ["11"],
}

class NaverAPI:
    """
    네이버 API와의 통신을 담당하는 서비스 클래스입니다.
    """
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_naver_access_token(self, code: str, state: str) -> str:
        """네이버로부터 액세스 토큰을 받아옵니다."""
        params = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": code,
            "state": state,
        }
        response = await self.client.get(settings.NAVER_TOKEN_URL, params=params)
        response.raise_for_status()
        token_data = response.json()
        if "error" in token_data:
            raise Exception(f"Naver token error: {token_data['error_description']}")
        return token_data["access_token"]

    async def get_naver_user_profile(self, access_token: str) -> Dict[str, Any]:
        """네이버 사용자 프로필 정보를 가져옵니다."""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self.client.get(settings.NAVER_PROFILE_URL, headers=headers)
        response.raise_for_status()
        profile_data = response.json()
        if profile_data.get("resultcode") != "00":
            raise Exception("Failed to get user profile from Naver.")
        return profile_data["response"]

    async def _fetch_trend_data_for_age_group(
        self,
        keyword: str,
        start_date: str,
        end_date: str,
        age_codes: List[str],
    ) -> List[Dict]:
        """단일 연령대 그룹에 대한 검색어 트렌드 데이터를 네이버 API로부터 가져옵니다."""
        headers = {
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
            "Content-Type": "application/json",
        }
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "date",
            "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
            "ages": age_codes,
        }
        response = await self.client.post(
            settings.NAVER_DATALAB_URL, headers=headers, data=json.dumps(body)
        )

        if response.status_code != 200:
            logger.error(f"Naver API Error: {response.status_code} - {response.text}")

        response.raise_for_status()
        return response.json()["results"][0]["data"]

    async def get_combined_trend_data(
        self, keyword: str
    ) -> trend_schema.TrendResponse:
        """
        모든 연령대 그룹의 검색어 트렌드 데이터를 취합하여 최종 응답 형태로 가공합니다.
        """
        today = date.today()
        end_date = today - timedelta(days=1)
        start_date = today - timedelta(days=8)
        
        # 비동기 작업을 병렬로 실행
        tasks = [
            self._fetch_trend_data_for_age_group(
                keyword, start_date.isoformat(), end_date.isoformat(), codes
            )
            for codes in AGE_GROUPS.values()
        ]
        results_by_age = await asyncio.gather(*tasks)

        # 결과 취합
        combined_results: Dict[str, Dict] = {
            (start_date + timedelta(days=i)).isoformat(): {
                "date": (start_date + timedelta(days=i)).isoformat(), "trends": {}
            }
            for i in range(7)
        }

        for age_key, age_data in zip(AGE_GROUPS.keys(), results_by_age):
            for daily_data in age_data:
                date_str = daily_data["period"]
                if date_str in combined_results:
                    combined_results[date_str]["trends"][age_key] = daily_data["ratio"]

        return trend_schema.TrendResponse(
            keyword=keyword,
            startDate=start_date,
            endDate=end_date,
            results=list(combined_results.values()),
        )