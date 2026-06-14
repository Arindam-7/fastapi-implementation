from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.user import UserCreate, UserResponse
from src.services.user import UserService
from src.api.dependencies import RoleChecker
from src.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Public route handling secure registration workflows."""
    service = UserService(db)
    return await service.register_user(user_in)

@router.get("/admin-dashboard", response_model=UserResponse)
async def get_admin_dashboard(
    current_admin: User = Depends(RoleChecker(allowed_roles=["admin"]))
) -> User:
    """Exclusive endpoint protected with granular RBAC requirements."""
    return current_admin