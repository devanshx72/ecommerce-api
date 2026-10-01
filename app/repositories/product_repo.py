from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:

    def get_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).options(
            joinedload(Product.category_rel)
        ).filter(Product.id == product_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Product]:
        return db.query(Product).filter(Product.name == name).first()

    def get_query(
        self,
        db: Session,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = False,
        search: Optional[str] = None
    ):
        """
        Returns a query object — NOT executed yet.
        Caller decides whether to paginate or get all.
        This is the key difference from before!
        """
        query = db.query(Product).options(
            joinedload(Product.category_rel)
        )

        # Search by name or description
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Product.name.ilike(search_term) |
                Product.description.ilike(search_term)
            )

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        if in_stock:
            query = query.filter(Product.stock > 0)

        return query

    def get_all(
        self,
        db: Session,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = False,
        search: Optional[str] = None
    ) -> list[Product]:
        return self.get_query(
            db, category_id, min_price, max_price, in_stock, search
        ).all()

    def create(self, db: Session, product_data: ProductCreate) -> Product:
        db_product = Product(**product_data.model_dump())
        db_product.is_available = product_data.stock > 0
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    def update(self, db: Session, product: Product, update_data: dict) -> Product:
        for field, value in update_data.items():
            setattr(product, field, value)
        if "stock" in update_data:
            product.is_available = product.stock > 0
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product: Product) -> None:
        db.delete(product)
        db.commit()


product_repo = ProductRepository()