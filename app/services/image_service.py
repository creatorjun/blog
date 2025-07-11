# app/services/image_service.py

import httpx
from typing import Optional
from app.core import config

image_service_toggler = 0

async def _fetch_image_from_pexels(query: str) -> Optional[str]:
    """Pexels API에서 이미지 검색"""
    if not config.PEXELS_API_KEY:
        return None
        
    api_url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "page": 1, "orientation": "landscape"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["large"]
        except Exception as e:
            print(f"Pexels API 에러: {e}")
    return None

async def _fetch_image_from_unsplash(query: str) -> Optional[str]:
    """Unsplash API에서 이미지 검색"""
    if not config.UNSPLASH_ACCESS_KEY:
        return None
        
    api_url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {config.UNSPLASH_ACCESS_KEY}"}
    params = {"query": query, "per_page": 1, "page": 1, "orientation": "landscape"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"Unsplash API 에러: {e}")
    return None

async def fetch_stock_image(query: str) -> Optional[str]:
    """Pexels와 Unsplash를 번갈아가며 이미지 검색"""
    global image_service_toggler
    
    if image_service_toggler == 0:
        print(f"Pexels에서 '{query}' 이미지 검색 중...")
        image_url = await _fetch_image_from_pexels(query)
        image_service_toggler = 1
    else:
        print(f"Unsplash에서 '{query}' 이미지 검색 중...")
        image_url = await _fetch_image_from_unsplash(query)
        image_service_toggler = 0
        
    return image_url