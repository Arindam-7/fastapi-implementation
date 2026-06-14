from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserBase(BaseModel):
    """Shared fields for User requests and responses."""
    email: EmailStr
    is_active: bool = True
    role: str = Field(default="viewer", max_length=50)

class UserCreate(UserBase):
    """Input contract required for user registration."""
    password: str = Field(..., min_length=8, description="Plaintext password must be at least 8 characters.")

class UserResponse(UserBase):
    """Output contract returned to clients. Excludes sensitive security fields."""
    id: int
    
    # Enables Pydantic to read SQLAlchemy ORM models directly
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    """Output contract for successful JWT authentication."""
    access_token: str
    token_type: str = "bearer"
