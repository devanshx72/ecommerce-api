from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.category_repo import category_repo
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:

    def get_all(self, db: Session):
        return category_repo.get_all(db)

    def get_by_id(self, db: Session, category_id: int):
        category = category_repo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found"
            )
        return category

    def create(self, db: Session, category_data: CategoryCreate):
        if category_repo.get_by_name(db, category_data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_data.name}' already exists"
            )
        return category_repo.create(db, category_data)

    def update(self, db: Session, category_id: int, category_data: CategoryUpdate):
        category = category_repo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found"
            )
        update_data = category_data.model_dump(exclude_unset=True)
        return category_repo.update(db, category, update_data)

    def delete(self, db: Session, category_id: int):
        category = category_repo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found"
            )
        category_repo.delete(db, category)


category_service = CategoryService()