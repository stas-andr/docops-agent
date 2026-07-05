from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes import router
from logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="DocOps Agent", version="0.1.0")
app.include_router(router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
