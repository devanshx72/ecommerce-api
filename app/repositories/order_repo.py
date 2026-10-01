from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.models.order import Order, OrderItem, OrderStatus


class OrderRepository:

    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.id == order_id).first()

    def get_user_orders(self, db: Session, user_id: int) -> list[Order]:
        return db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.user_id == user_id)\
         .order_by(Order.created_at.desc()).all()

    def get_all_orders(self, db: Session) -> list[Order]:
        """Admin — get all orders."""
        return db.query(Order).options(
            joinedload(Order.items)
        ).order_by(Order.created_at.desc()).all()

    def create_order(
        self,
        db: Session,
        user_id: int,
        total_amount: float,
        shipping_address: str,
        items_data: list[dict]
    ) -> Order:
        """
        Create order with items in a single transaction.
        items_data = [
            {product_id, product_name, unit_price, quantity, subtotal}
        ]
        """
        try:
            # Create order
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                shipping_address=shipping_address,
                status=OrderStatus.pending
            )
            db.add(order)
            db.flush()  # flush to get order.id without committing

            # Create order items
            for item_data in items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    **item_data
                )
                db.add(order_item)

            db.commit()
            db.refresh(order)
            return order

        except Exception:
            db.rollback()  # rollback everything if any error
            raise

    def update_status(self, db: Session, order: Order, status: OrderStatus) -> Order:
        order.status = status
        db.commit()
        db.refresh(order)
        return order


order_repo = OrderRepository()