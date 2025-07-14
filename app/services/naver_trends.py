import httpx
import json
import asyncio
from datetime import date, timedelta
from typing import List, Dict

from ..core.config import NAVER_DATALAB_CLIENT_ID, NAVER_DATALAB_CLIENT_SECRET
from ..schemas import trend as trend_schema

# 네이버 데이터랩 API URL
NAVER_API_URL = "https://openapi.naver.com/v1/datalab/search"

# ⭐️ 수정: 조회할 연령대 그룹을 네이버 API 코드에 맞게 재정의
AGE_GROUPS = {
    "10s": ["2", "3"],          # 13-18, 19-24세
    "20s": ["4", "5"],          # 25-29, 30-34세
    "30s": ["6", "7"],          # 35-39, 40-44세
    "40s": ["8", "9"],          # 45-49, 50-54세
    "50s": ["10"],              # 55-59세
    "60s+": ["11"],             # 60세 이상
}

# ⭐️ 수정: age_codes를 리스트로 받도록 변경
async def fetch_trend_data(
    session: httpx.AsyncClient,
    keyword: str,
    start_date: str,
    end_date: str,
    age_codes: List[str],
) -> List[Dict]:
    """
    단일 연령대 그룹에 대한 검색어 트렌드 데이터를 네이버 API로부터 비동기적으로 가져옵니다.
    """
    headers = {
        "X-Naver-Client-Id": NAVER_DATALAB_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_DATALAB_CLIENT_SECRET,
        "Content-Type": "application/json",
    }
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
        "ages": age_codes,
    }
    response = await session.post(NAVER_API_URL, headers=headers, data=json.dumps(body))
    
    # API 호출 실패 시, 네이버가 보낸 에러 메시지를 포함하여 로그 출력
    if response.status_code != 200:
        print(f"Naver API Error: {response.status_code} - {response.text}")
    
    response.raise_for_status()
    return response.json()["results"][0]["data"]

async def get_combined_trend_data(keyword: str) -> trend_schema.TrendResponse:
    """
    모든 연령대 그룹의 검색어 트렌드 데이터를 취합하여 최종 응답 형태로 가공합니다.
    """
    today = date.today()
    end_date = today - timedelta(days=1)
    start_date = today - timedelta(days=8)

    combined_results: Dict[str, Dict] = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        combined_results[date_str] = {"date": date_str, "trends": {}}
        current_date += timedelta(days=1)

    async with httpx.AsyncClient() as session:
        # ⭐️ 수정: 새로운 AGE_GROUPS 딕셔너리를 사용하여 tasks 생성
        tasks = [
            fetch_trend_data(
                session,
                keyword,
                start_date.isoformat(),
                end_date.isoformat(),
                codes,
            )
            for codes in AGE_GROUPS.values()
        ]
        results_by_age = await asyncio.gather(*tasks)

    # ⭐️ 수정: 결과를 조합하는 로직 변경
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