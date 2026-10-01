from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, value):
        # Strip whitespace
        value = value.strip()
        # No spaces in username
        if ' ' in value:
            raise ValueError('Username cannot contain spaces')
        return value.lower()  # store as lowercase


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for returning user data."""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for returning JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse