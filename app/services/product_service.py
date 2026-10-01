from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.repositories.product_repo import product_repo
from app.repositories.category_repo import category_repo
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.pagination import paginate


class ProductService:

    def get_all(
        self,
        db: Session,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = False,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ):
        """Get products with filters + pagination + search."""
        query = product_repo.get_query(
            db, category_id, min_price, max_price, in_stock, search
        )
        return paginate(query, page, limit)

    def get_by_id(self, db: Session, product_id: int):
        product = product_repo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        return product

    def create(self, db: Session, product_data: ProductCreate):
        if product_repo.get_by_name(db, product_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product_data.name}' already exists"
            )
        if not category_repo.get_by_id(db, product_data.category_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {product_data.category_id} not found"
            )
        return product_repo.create(db, product_data)

    def update(self, db: Session, product_id: int, product_data: ProductUpdate):
        product = product_repo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        update_data = product_data.model_dump(exclude_unset=True)
        if "category_id" in update_data:
            if not category_repo.get_by_id(db, update_data["category_id"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category {update_data['category_id']} not found"
                )
        return product_repo.update(db, product, update_data)

    def delete(self, db: Session, product_id: int):
        product = product_repo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        product_repo.delete(db, product)


product_service = ProductService()