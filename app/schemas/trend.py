from pydantic import BaseModel, Field
from datetime import date

class TrendDataPoint(BaseModel):
    date: date
    # ⭐️ 이 부분의 int를 float으로 수정합니다.
    trends: dict[str, float]

class TrendResponse(BaseModel):
    keyword: str
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")
    results: list[TrendDataPoint]