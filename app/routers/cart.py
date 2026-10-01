from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cart import AddToCartRequest, UpdateCartItemRequest, CartResponse
from app.services.cart_service import cart_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get current user's cart."""
    return cart_service.get_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse)
def add_to_cart(
    request: AddToCartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Add product to cart."""
    return cart_service.add_to_cart(db, current_user.id, request)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    request: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Update quantity of cart item."""
    return cart_service.update_item(db, current_user.id, item_id, request.quantity)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Remove item from cart."""
    return cart_service.remove_item(db, current_user.id, item_id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Clear entire cart."""
    cart_service.clear_cart(db, current_user.id)