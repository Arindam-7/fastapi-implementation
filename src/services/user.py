from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate
from src.models.user import User
from src.core.security import get_password_hash
from src.core.exceptions import HTTPExceptionCustom

class UserService:
    def __init__(self, db: AsyncSession) -> None:
        """
        Domain service coordinating orchestration, business logic, and transaction sequencing.
        """
        self.user_repo = UserRepository(db)

    async def register_user(self, user_in: UserCreate) -> User:
        # Enforce business invariant: email uniqueness
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPExceptionCustom(status_code=400, detail="Email is already registered.")
        
        # Transform the Pydantic DTO to a dictionary and sanitize the password field
        user_data = user_in.model_dump()
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)
        
        # Delegate DB persistence to the data access layer
        return await self.user_repo.create(user_data)