import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        logger.exception(f'Error in custom_http_exception_handler: {exc}')
        return JSONResponse(
            status_code=exc.status_code,  # Use the original exception's status_code
            content={'message': exc.detail},  # Use the original exception's detail
        )
