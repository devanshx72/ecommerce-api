from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.order import OrderStatus


class PlaceOrderRequest(BaseModel):
    """Place order from cart."""
    shipping_address: str = Field(..., min_length=10, max_length=500)


class UpdateOrderStatusRequest(BaseModel):
    """Admin updates order status."""
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    shipping_address: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True