from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False, index=True)

    email = Column(String(255), unique=True, nullable=False, index=True)

    # We NEVER store plain passwords
    # Always store the hash
    hashed_password = Column(String(255), nullable=False)

    # is_active — soft delete pattern
    # Instead of deleting users we deactivate them
    # This preserves order history, audit trails etc
    is_active = Column(Boolean, default=True)

    # is_admin — role based access
    # True = admin can do everything
    # False = regular customer
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())