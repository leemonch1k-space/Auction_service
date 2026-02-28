from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.exceptions import BaseUserException
from src.routers import (
    auth_router,
    auction_router
)
app = FastAPI()

app.include_router(auth_router)
app.include_router(auction_router)


@app.exception_handler(BaseUserException)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"Error": "Validation error", "detail": str(exc)},
    )
