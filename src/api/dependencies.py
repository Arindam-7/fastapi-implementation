import jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.exceptions import HTTPExceptionCustom
from src.repositories.user import UserRepository
from src.models.user import User

# This automatically integrates a token authorization field in FastAPI's Swagger UI docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Reusable dependency that extracts, decodes, and validates an incoming JWT token,
    returning the database record for the authenticated user.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPExceptionCustom(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token token context: missing subject attribute."
            )
    except (jwt.PyJWTError, Exception):
        raise HTTPExceptionCustom(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials: token is corrupted or expired."
        )
        
    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if not user:
        raise HTTPExceptionCustom(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User identity associated with this token does not exist."
        )
    return user


class RoleChecker:
    """
    An enterprise RBAC guard factory. Generates endpoint-level access controls 
    by matching the current user's role against permitted values.
    """
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPExceptionCustom(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access Denied: Required privilege level not met. Allowed: {self.allowed_roles}"
            )
        return current_user