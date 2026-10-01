from sqlalchemy.orm import Session
from typing import Optional
from app.models.category import Category
from app.schemas.category import CategoryCreate


class CategoryRepository:

    def get_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

    def get_all(self, db: Session) -> list[Category]:
        return db.query(Category).all()

    def create(self, db: Session, category_data: CategoryCreate) -> Category:
        db_category = Category(**category_data.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    def update(self, db: Session, category: Category, update_data: dict) -> Category:
        for field, value in update_data.items():
            setattr(category, field, value)
        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, category: Category) -> None:
        db.delete(category)
        db.commit()


category_repo = CategoryRepository()