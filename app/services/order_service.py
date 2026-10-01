from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.order_repo import order_repo
from app.repositories.cart_repo import cart_repo
from app.repositories.product_repo import product_repo
from app.schemas.order import PlaceOrderRequest
from app.models.order import OrderStatus


class OrderService:

    def place_order(self, db: Session, user_id: int, request: PlaceOrderRequest):
        """
        Place order from cart.
        Steps:
        1. Get cart — must have items
        2. Validate all products still available
        3. Check stock for all items
        4. Create order with price snapshot
        5. Reduce product stock
        6. Clear cart
        """
        # Get cart
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        if not cart or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )

        # Validate all items and build order data
        items_data = []
        total_amount = 0.0

        for cart_item in cart.items:
            product = product_repo.get_by_id(db, cart_item.product_id)

            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {cart_item.product_id} no longer exists"
                )
            if not product.is_available:
                raise HTTPException(
                    status_code=400,
                    detail=f"'{product.name}' is no longer available"
                )
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {product.stock} of '{product.name}' in stock"
                )

            subtotal = product.price * cart_item.quantity
            total_amount += subtotal

            # Price SNAPSHOT — store current price
            items_data.append({
                "product_id": product.id,
                "product_name": product.name,
                "unit_price": product.price,  # snapshot!
                "quantity": cart_item.quantity,
                "subtotal": round(subtotal, 2)
            })

        # Create order in DB
        order = order_repo.create_order(
            db=db,
            user_id=user_id,
            total_amount=round(total_amount, 2),
            shipping_address=request.shipping_address,
            items_data=items_data
        )

        # Reduce stock for each product
        for cart_item in cart.items:
            product = product_repo.get_by_id(db, cart_item.product_id)
            new_stock = product.stock - cart_item.quantity
            product_repo.update(db, product, {
                "stock": new_stock,
                "is_available": new_stock > 0
            })

        # Clear cart after order placed
        cart_repo.clear_cart(db, cart)

        return order

    def get_my_orders(self, db: Session, user_id: int):
        return order_repo.get_user_orders(db, user_id)

    def get_order(self, db: Session, order_id: int, user_id: int):
        order = order_repo.get_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        # Users can only see their own orders
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your order"
            )
        return order

    def get_all_orders(self, db: Session):
        """Admin only."""
        return order_repo.get_all_orders(db)

    def update_status(self, db: Session, order_id: int, new_status: OrderStatus):
        """Admin updates order status."""
        order = order_repo.get_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order_repo.update_status(db, order, new_status)


order_service = OrderService()