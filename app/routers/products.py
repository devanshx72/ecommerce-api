from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.pagination import PaginatedResponse
from app.services.product_service import product_service
from app.dependencies import get_current_user, get_admin_user
from app.utils.file_upload import save_product_image, delete_product_image, get_image_url

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return product_service.create(db, product)


@router.get("/")
def get_products(
    # Filters
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    in_stock: bool = Query(False),
    # Search
    search: Optional[str] = Query(None, min_length=1),
    # Pagination
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get products with:
    - Filtering (category, price range, stock)
    - Search (name or description)
    - Pagination (page, limit)

    Examples:
    GET /products?search=iPhone
    GET /products?category_id=1&in_stock=true
    GET /products?min_price=1000&max_price=50000&page=2&limit=5
    """
    return product_service.get_all(
        db=db,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        search=search,
        page=page,
        limit=limit
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_by_id(db, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return product_service.update(db, product_id, product_data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):
    product_service.delete(db, product_id)
    
@router.post("/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user),
    file: UploadFile = File(...)
):
    """Upload image for a product. Admin only."""
    from app.repositories.product_repo import product_repo

    product = product_service.get_by_id(db, product_id)

    if product.image_url:
        old_filename = product.image_url.split("/")[-1]
        delete_product_image(old_filename)

    filename = await save_product_image(file)
    image_url = get_image_url(request, filename)

    return product_repo.update(db, product, {"image_url": image_url})