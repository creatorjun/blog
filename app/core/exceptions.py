# app/core/exceptions.py (신규 파일)

class CustomException(Exception):
    """
    모든 커스텀 예외의 기반이 되는 부모 클래스입니다.
    status_code와 detail 메시지를 기본 속성으로 가집니다.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

# --- 비즈니스 관련 예외들 ---

class UserNotFoundError(CustomException):
    """사용자를 찾지 못했을 때 발생하는 예외"""
    def __init__(self):
        super().__init__(status_code=404, detail="사용자를 찾을 수 없습니다.")

class InvalidTokenError(CustomException):
    """토큰이 유효하지 않거나 잘못되었을 때 발생하는 예외"""
    def __init__(self):
        super().__init__(status_code=401, detail="유효하지 않은 토큰입니다.")

class NaverAuthError(CustomException):
    """네이버 인증 과정에서 문제가 발생했을 때 던지는 예외"""
    def __init__(self, detail: str = "네이버 인증에 실패했습니다."):
        super().__init__(status_code=400, detail=detail)