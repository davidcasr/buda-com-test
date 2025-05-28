from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.exceptions.currency_exceptions import CurrencyException
import logging
import traceback
from typing import Union

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except CurrencyException as e:
        logger.error(f"Currency error: {str(e)}", extra={
            "status_code": e.status_code,
            "details": e.details,
            "path": request.url.path
        })
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.message,
                "details": e.details,
                "path": request.url.path
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra={
            "traceback": traceback.format_exc(),
            "path": request.url.path
        })
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "path": request.url.path
            }
        ) 