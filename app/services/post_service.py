# app/services/post_service.py

import json
import google.generativeai as genai
from typing import List, Dict
from app.core import config
from . import news_service, image_service, email_service # from app.services -> from .

# Gemini API 설정
genai.configure(api_key=config.GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')

last_processed_cache: Dict[str, str] = {}

def generate_curation_prompt(titles: List[str]) -> str:
    """AI가 화제성 있는 뉴스 주제를 선정하기 위한 프롬프트를 생성합니다."""
    titles_str = "\n".join(f"- {title}" for title in titles)
    return f"""# [역할]
당신은 수많은 뉴스 속에서 독자의 시선을 사로잡을 '진짜' 기사를 골라내는 능력이 탁월한 베테랑 디지털 콘텐츠 편집장입니다.
# [목표]
아래에 제공된 최신 뉴스 헤드라인 목록을 보고, 이 중에서 가장 화제성이 높고, 논쟁적이며, 독자들이 가장 궁금해할 만한 단 하나의 기사를 선정하는 것입니다.
# [핵심 지시사항]
1. 각 헤드라인의 잠재적인 파급력, 대중의 관심도, 시의성을 종합적으로 고려하세요.
2. 가장 매력적이라고 판단되는 기사의 제목 **단 하나만**을 선택하세요.
3. 다른 설명, 부연, 따옴표 없이 **오직 선택한 기사의 원본 제목 그대로** 응답해야 합니다.
# [뉴스 헤드라인 목록]
{titles_str}"""

def generate_post_prompt_from_single_article(article: dict) -> str:
    """AI가 블로그 포스트를 생성하기 위한 프롬프트를 생성합니다."""
    article_str = json.dumps(article, ensure_ascii=False, indent=2)
    return f"""# [역할]
당신은 글의 맥락을 완벽하게 이해하고, 그에 어울리는 시각 자료를 배치하는 능력이 탁월한 전문 콘텐츠 디렉터입니다.
# [목표]
제공된 뉴스 기사 하나를 바탕으로, 독자의 몰입감을 극대화하는 완벽한 블로그 포스트를 생성하는 것입니다.
# [핵심 지시사항]
1. **심층 분석 및 글 작성:** 기사를 심층 분석하여 배경, 영향, 전망, 인사이트를 담아 블로그 포스트의 각 섹션을 작성하세요.
2. **이미지 삽입 위치 결정:** 작성한 `main_body` 내용 중, 가장 적절하다고 생각되는 위치에 **단 한번만** `[IMAGE]` 라는 태그를 삽입하세요.
3. **이미지 검색 키워드 제안:** 완성된 글 전체의 주제를 가장 잘 나타내는 **영어 2~3단어**의 스톡 이미지 검색용 키워드를 제안하세요.
4. **JSON 형식 준수:** 최종 결과물은 반드시 아래 '출력 JSON 형식'을 따라야 합니다.
5. **한국어 답변 강제**: `image_search_keyword` 필드를 제외한 모든 응답은 반드시 **한국어**로 작성되어야 합니다.
# [출력 JSON 형식]
{{
  "blog_title": "기사 내용을 재해석한, 흥미롭고 SEO에 최적화된 블로그 제목",
  "introduction": "독자가 글을 끝까지 읽고 싶게 만드는 매력적인 서론",
  "main_body": "내용의 흐름 상 가장 적절한 위치에 `[IMAGE]` 태그가 삽입된, 마크다운으로 구조화된 본문",
  "key_takeaways": ["핵심 메시지 1", "핵심 메시지 2", "핵심 메시지 3"],
  "conclusion": "본문 내용을 요약하고 마무리하는 결론",
  "suggested_tags": ["콘텐츠와 관련된 추천 해시태그 1", "태그 2", "태그 3"],
  "image_search_keyword": "AI가 제안하는 2~3단어의 영어 검색 키워드"
}}
# [분석할 뉴스 기사]
{article_str}"""

async def create_curated_blog_post(section_value: str) -> dict:
    """AI가 주제를 선정하고 포스트를 생성하는 전체 워크플로우를 담당합니다."""
    all_news_articles = await news_service.fetch_naver_news(section_value, display=30)
    if not all_news_articles:
        return {"error": "no_news", "detail": f"'{section_value}' 섹션에서 뉴스를 찾는 데 실패했습니다."}
    
    titles = [article['title'] for article in all_news_articles]
    curation_prompt = generate_curation_prompt(titles)
    
    try:
        curation_response = await gemini_model.generate_content_async(curation_prompt)
        chosen_title = curation_response.text.strip()
    except Exception as e:
        return {"error": "curation_failed", "detail": f"AI 모델 주제 선정 중 에러: {e}"}
    
    chosen_article = next((article for article in all_news_articles if article['title'] == chosen_title), None)
    if not chosen_article:
        return {"error": "no_match", "detail": "AI가 선택한 제목과 일치하는 기사를 찾을 수 없습니다."}
    
    last_processed_link = last_processed_cache.get(section_value)
    if last_processed_link == chosen_article.get("link"):
        return {"error": "duplicate", "detail": "새로운 뉴스가 없습니다. AI가 선택한 기사가 이전에 처리한 기사와 동일합니다."}

    post_prompt = generate_post_prompt_from_single_article(chosen_article)
    
    try:
        post_response = await gemini_model.generate_content_async(post_prompt)
        cleaned_text = post_response.text.strip().replace("```json", "").replace("```", "")
        blog_post_data = json.loads(cleaned_text)
        blog_post_data['original_article_link'] = chosen_article.get('link')
        
        image_query = blog_post_data.get('image_search_keyword', chosen_title)
        featured_image = await image_service.fetch_stock_image(image_query)
        blog_post_data['featured_image_url'] = featured_image
        
        last_processed_cache[section_value] = chosen_article.get("link")
        
        return email_service.send_post_via_email(blog_post_data)
        
    except json.JSONDecodeError:
        return {"error": "parsing_failed", "detail": "AI의 포스트 응답을 JSON으로 파싱하는데 실패했습니다."}
    except Exception as e:
        return {"error": "generation_failed", "detail": f"AI 모델 포스트 생성 중 에러: {e}"}