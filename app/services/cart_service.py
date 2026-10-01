from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.cart_repo import cart_repo
from app.repositories.product_repo import product_repo
from app.schemas.cart import AddToCartRequest, CartResponse, CartItemResponse


class CartService:

    def get_or_create_cart(self, db: Session, user_id: int):
        """Get existing cart or create new one."""
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        if not cart:
            cart = cart_repo.create_cart(db, user_id)
            # Reload with items
            cart = cart_repo.get_cart_by_user_id(db, user_id)
        return cart

    def get_cart(self, db: Session, user_id: int):
        cart = self.get_or_create_cart(db, user_id)
        return self._build_cart_response(cart)

    def add_to_cart(self, db: Session, user_id: int, request: AddToCartRequest):
        # Validate product exists and is available
        product = product_repo.get_by_id(db, request.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        if not product.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is not available"
            )
        if product.stock < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock} items in stock"
            )

        # Get or create cart
        cart = self.get_or_create_cart(db, user_id)

        # Check if product already in cart
        existing_item = cart_repo.get_cart_item(db, cart.id, request.product_id)

        if existing_item:
            # Update quantity
            new_qty = existing_item.quantity + request.quantity
            if new_qty > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot add more. Only {product.stock} in stock"
                )
            cart_repo.update_item_quantity(db, existing_item, new_qty)
        else:
            # Add new item
            cart_repo.add_item(db, cart.id, request.product_id, request.quantity)

        # Return updated cart
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        return self._build_cart_response(cart)

    def update_item(self, db: Session, user_id: int, item_id: int, quantity: int):
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        item = cart_repo.get_cart_item_by_id(db, item_id)
        if not item or item.cart_id != cart.id:
            raise HTTPException(status_code=404, detail="Item not found in your cart")

        # Validate stock
        product = product_repo.get_by_id(db, item.product_id)
        if quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} items in stock"
            )

        cart_repo.update_item_quantity(db, item, quantity)
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        return self._build_cart_response(cart)

    def remove_item(self, db: Session, user_id: int, item_id: int):
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        item = cart_repo.get_cart_item_by_id(db, item_id)
        if not item or item.cart_id != cart.id:
            raise HTTPException(status_code=404, detail="Item not found in your cart")

        cart_repo.remove_item(db, item)
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        return self._build_cart_response(cart)

    def clear_cart(self, db: Session, user_id: int):
        cart = cart_repo.get_cart_by_user_id(db, user_id)
        if cart:
            cart_repo.clear_cart(db, cart)

    def _build_cart_response(self, cart) -> dict:
        """Build cart response with calculated fields."""
        items = []
        total_amount = 0.0
        total_items = 0

        for item in cart.items:
            subtotal = item.product.price * item.quantity
            total_amount += subtotal
            total_items += item.quantity
            items.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": item.product,
                "subtotal": round(subtotal, 2)
            })

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "items": items,
            "total_items": total_items,
            "total_amount": round(total_amount, 2)
        }


cart_service = CartService()