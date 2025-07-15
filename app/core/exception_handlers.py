# app/core/exception_handlers.py (신규 파일)

from fastapi import Request, status
from fastapi.responses import JSONResponse

from .exceptions import CustomException

async def custom_exception_handler(request: Request, exc: CustomException):
    """
    CustomException을 상속받는 모든 예외에 대한 핸들러입니다.
    예외 객체에 정의된 상태 코드와 메시지를 사용하여 JSON 응답을 생성합니다.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    처리되지 않은 모든 예외를 잡아 500 Internal Server Error로 응답합니다.
    프로덕션 환경에서는 에러 로깅을 추가하는 것이 중요합니다.
    """
    # 여기에 에러 로깅 로직을 추가할 수 있습니다 (예: Sentry, Datadog)
    # logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "서버 내부 오류가 발생했습니다."},
    )