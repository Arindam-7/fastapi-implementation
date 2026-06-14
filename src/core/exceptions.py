from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class HTTPExceptionCustom(Exception):
    """Custom exception class for fine-grained control over enterprise application errors."""
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail

def register_exception_handlers(app: FastAPI) -> None:
    """Attaches unified corporate error mapping schemas to the active FastAPI context."""
    @app.exception_handler(HTTPExceptionCustom)
    async def custom_http_exception_handler(request: Request, exc: HTTPExceptionCustom) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False, 
                "error": {
                    "message": exc.detail
                }
            },
        )