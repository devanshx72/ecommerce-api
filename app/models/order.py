from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# Order status as Python enum
# Using enum ensures only valid values stored in DB
class OrderStatus(str, enum.Enum):
    pending = "pending"       # just placed
    confirmed = "confirmed"   # payment received
    shipped = "shipped"       # out for delivery
    delivered = "delivered"   # delivered to customer
    cancelled = "cancelled"   # cancelled


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Total amount at time of order
    total_amount = Column(Float, nullable=False)

    # Status using enum — only valid values allowed
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.pending,
        nullable=False
    )

    # Shipping address — stored as plain text
    # In production you'd have a separate Address table
    shipping_address = Column(String(500), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="orders",  lazy="joined")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # ── PRICE SNAPSHOT ── very important!
    # We store price AT TIME OF ORDER
    # If product price changes later
    # order history stays accurate
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Total for this line item
    # unit_price * quantity
    subtotal = Column(Float, nullable=False)

    # Store product name too — in case product is deleted later
    product_name = Column(String(255), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")