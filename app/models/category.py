from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # ── Relationship ──
    # This tells SQLAlchemy:
    # "A Category has MANY Products"
    # back_populates="category" connects to
    # the 'category' relationship in Product model
    # lazy="dynamic" means products are NOT loaded
    # automatically — only when you access .products
    products = relationship(
        "Product",
        back_populates="category_rel",
        lazy="dynamic"
    )