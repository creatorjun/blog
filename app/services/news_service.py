# app/services/news_service.py

import httpx
from typing import List
from app.core import config

async def fetch_naver_news(query: str, display: int = 10) -> List[dict]:
    """네이버 뉴스 API를 호출하여 뉴스 리스트를 반환합니다."""
    api_url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": config.NAVER_CLIENT_ID, "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET}
    params = {"query": query, "display": display, "sort": "date"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            
            news_list = []
            for item in items:
                news_list.append({
                    "title": item.get('title', '').replace("<b>", "").replace("</b>", "").replace("&quot;", '"'),
                    "description": item.get('description', '').replace("<b>", "").replace("</b>", "").replace("&quot;", '"'),
                    "link": item.get('originallink', item.get('link')),
                    "pubDate": item.get('pubDate')
                })
            return news_list
        except Exception as e:
            print(f"네이버 뉴스 호출 중 에러: {e}")
            return []