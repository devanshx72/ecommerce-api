from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    # Each user has exactly ONE cart
    # unique=True enforces one cart per user at DB level
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    # cascade="all, delete-orphan" means:
    # if cart is deleted → all cart items deleted too
    # if cart item is removed from items list → deleted from DB


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # How many of this product in cart
    quantity = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")