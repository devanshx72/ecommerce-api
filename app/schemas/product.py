from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: int = Field(..., gt=0)   # ← now takes ID not string

    @field_validator('name')
    @classmethod
    def name_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError('Name cannot be blank')
        return value.strip()


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = Field(None, gt=0)


class CategoryInProduct(BaseModel):
    """Nested category info inside product response."""
    id: int
    name: str

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_available: bool
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    category_id: Optional[int]
    category_rel: Optional[CategoryInProduct] = None  # nested object!

    class Config:
        from_attributes = True