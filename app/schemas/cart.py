from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddToCartRequest(BaseModel):
    """Add a product to cart."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)  # max 100 of same item


class UpdateCartItemRequest(BaseModel):
    """Update quantity of a cart item."""
    quantity: int = Field(..., gt=0, le=100)


class CartItemProductInfo(BaseModel):
    """Product info nested inside cart item."""
    id: int
    name: str
    price: float
    is_available: bool

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: CartItemProductInfo
    subtotal: float  # calculated field

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse] = []
    total_items: int      # total quantity of all items
    total_amount: float   # total price

    class Config:
        from_attributes = True