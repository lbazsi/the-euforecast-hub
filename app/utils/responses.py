from fastapi import HTTPException

def error_response(code: str, message: str, status_code: int = 400, details: dict | None = None):
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": {"code": code, "message": message, "details": details or {}}
        }
    )
