from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order import PlaceOrderRequest, OrderResponse, UpdateOrderStatusRequest
from app.services.order_service import order_service
from app.dependencies import get_current_user, get_admin_user
from app.utils.email import send_order_confirmation_email, send_status_update_email

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    request: PlaceOrderRequest,
    background_tasks: BackgroundTasks,  # ← inject BackgroundTasks
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Place order from cart.
    Response is immediate.
    Email sends in background.
    """
    order = order_service.place_order(db, current_user.id, request)

    # Prepare items data for email
    items_for_email = [
        {
            "product_name": item.product_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.subtotal
        }
        for item in order.items
    ]

    # Add email task to background
    # This runs AFTER response is sent to client
    background_tasks.add_task(
        send_order_confirmation_email,
        user_email=current_user.email,
        username=current_user.username,
        order_id=order.id,
        total_amount=order.total_amount,
        items=items_for_email,
        shipping_address=order.shipping_address
    )

    return order


@router.get("/my", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return order_service.get_my_orders(db, current_user.id)


@router.get("/my/{order_id}", response_model=OrderResponse)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return order_service.get_order(db, order_id, current_user.id)


@router.get("/admin/all", response_model=list[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):
    return order_service.get_all_orders(db)


@router.patch("/admin/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    background_tasks: BackgroundTasks,  # ← inject here too
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):
    """Admin updates order status — sends email to customer."""
    order = order_service.update_status(db, order_id, request.status)

    # Get customer info for email
    background_tasks.add_task(
        send_status_update_email,
        user_email=order.user.email,
        username=order.user.username,
        order_id=order.id,
        new_status=request.status.value
    )

    return order