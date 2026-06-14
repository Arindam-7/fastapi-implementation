from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_password, create_access_token
from src.core.exceptions import HTTPExceptionCustom
from src.repositories.user import UserRepository
from src.schemas.user import TokenResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """
    Standard OAuth2-compliant login exchange.
    Validates form data credentials and returns an encrypted access token string.
    """
    repo = UserRepository(db)
    user = await repo.get_by_email(form_data.username)  # OAuth2 form uses 'username' field for login identifier
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPExceptionCustom(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid email or password credentials."
        )
    
    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}