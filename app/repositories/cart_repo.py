from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.models.cart import Cart, CartItem


class CartRepository:

    def get_cart_by_user_id(self, db: Session, user_id: int) -> Optional[Cart]:
        """Get cart with all items and product info loaded."""
        return db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.user_id == user_id).first()

    def create_cart(self, db: Session, user_id: int) -> Cart:
        """Create a new cart for user."""
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    def get_cart_item(self, db: Session, cart_id: int, product_id: int) -> Optional[CartItem]:
        """Get specific item in cart."""
        return db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        ).first()

    def get_cart_item_by_id(self, db: Session, item_id: int) -> Optional[CartItem]:
        return db.query(CartItem).filter(CartItem.id == item_id).first()

    def add_item(self, db: Session, cart_id: int, product_id: int, quantity: int) -> CartItem:
        """Add new item to cart."""
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_item_quantity(self, db: Session, item: CartItem, quantity: int) -> CartItem:
        """Update quantity of existing cart item."""
        item.quantity = quantity
        db.commit()
        db.refresh(item)
        return item

    def remove_item(self, db: Session, item: CartItem) -> None:
        """Remove item from cart."""
        db.delete(item)
        db.commit()

    def clear_cart(self, db: Session, cart: Cart) -> None:
        """Remove all items from cart."""
        for item in cart.items:
            db.delete(item)
        db.commit()


cart_repo = CartRepository()