from fastapi import Request, HTTPException, Response, status as HTTPStatus

from fastapi.responses import JSONResponse

from app.models.response import QueryResponse

from app.config import logger

class ErrorResponse(QueryResponse):
    error: str


class RequestError(HTTPException):
    ...

class RequestTimeoutError(RequestError):

    def __init__(self, error: str = "Request timed out"):
        super().__init__(HTTPStatus.HTTP_408_REQUEST_TIMEOUT, error)

class OpenStreetMapError(RequestError):

    def __init__(self, error: str = "OpenStreetMap error"):
        super().__init__(HTTPStatus.HTTP_502_BAD_GATEWAY, error)


async def request_error_handler(request: Request, error: RequestError) -> Response:
    logger.error(error.detail)

    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(query_url=str(request.url), error=error.detail).model_dump(mode='json')
    )
