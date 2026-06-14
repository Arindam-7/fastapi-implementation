from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base

class User(Base):
    """
    SQLAlchemy 2.0 Declarative Mapping for the 'users' table.
    Defines database layout and internal constraints.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # RBAC configuration field (e.g., 'admin', 'manager', 'viewer')
    role: Mapped[str] = mapped_column(String(50), default="viewer", nullable=False)
