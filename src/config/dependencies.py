import os
from typing import Any, AsyncGenerator, Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from src.config.settings import BaseAppSettings, get_settings
from src.database.engine import AsyncSessionLocal
from src.database.models import UserModel
from src.exceptions import TokenExpiredError, InvalidTokenError
from src.security import JWTAuthManagerInterface, JWTAuthManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/login/")

async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionLocal() as session:
        yield session

def get_jwt_manager(
    settings: Annotated[BaseAppSettings, Depends(get_settings)],
) -> JWTAuthManagerInterface:
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.JWT_SIGNING_ALGORITHM,
    )

async def get_authenticated_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_manager: Annotated[JWTAuthManagerInterface, Depends(get_jwt_manager)],
) -> type[UserModel] | None:
    try:
        user_data = jwt_manager.decode_access_token(token)
    except (TokenExpiredError, InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Invalid or expired"
        )

    user_id = user_data.get("user_id")

    return await db.get(
        UserModel,
        user_id,
        options=[joinedload(UserModel.group), joinedload(UserModel.collection)],
    )
