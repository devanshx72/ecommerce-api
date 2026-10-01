import pytest


class TestOrders:
    """Tests for order endpoints."""

    def test_place_order_empty_cart(self, client, auth_headers):
        """Cannot place order with empty cart."""
        response = client.post("/orders/", json={
            "shipping_address": "123 Main St, Bangalore 560001"
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "empty" in response.json()["error"]["message"].lower()

    def test_place_order_success(self, client, auth_headers, sample_product):
        """Successfully place order from cart."""
        # Add to cart
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)

        # Place order
        response = client.post("/orders/", json={
            "shipping_address": "123 Main St, Bangalore 560001"
        }, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["total_amount"] == sample_product["price"]
        assert len(data["items"]) == 1

    def test_order_clears_cart(self, client, auth_headers, sample_product):
        """After placing order cart should be empty."""
        # Add to cart
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)

        # Place order
        client.post("/orders/", json={
            "shipping_address": "123 Main St"
        }, headers=auth_headers)

        # Check cart is empty
        cart = client.get("/cart/", headers=auth_headers)
        assert cart.json()["items"] == []

    def test_order_reduces_stock(self, client, auth_headers, sample_product):
        """Placing order reduces product stock."""
        initial_stock = sample_product["stock"]
        quantity = 2

        # Add to cart
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": quantity
        }, headers=auth_headers)

        # Place order
        client.post("/orders/", json={
            "shipping_address": "123 Main St"
        }, headers=auth_headers)

        # Check stock reduced
        product = client.get(f"/products/{sample_product['id']}")
        assert product.json()["stock"] == initial_stock - quantity

    def test_order_price_snapshot(self, client, auth_headers, admin_user, sample_product):
        """Order stores price at time of purchase."""
        original_price = sample_product["price"]

        # Add to cart
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)

        # Change price BEFORE placing order
        client.patch(f"/products/{sample_product['id']}",
            json={"price": 999999.0},
            headers=admin_user
        )

        # Place order
        response = client.post("/orders/", json={
            "shipping_address": "123 Main St"
        }, headers=auth_headers)

        # Order should have ORIGINAL price — not new price
        order_item = response.json()["items"][0]
        assert order_item["unit_price"] == original_price

    def test_get_my_orders(self, client, auth_headers, sample_product):
        """User can see their orders."""
        # Add and order
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)
        client.post("/orders/", json={
            "shipping_address": "123 Main St"
        }, headers=auth_headers)

        # Get orders
        response = client.get("/orders/my", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_cannot_see_others_orders(self, client, auth_headers, admin_user, sample_product):
        """User cannot access other users orders."""
        # Admin places order
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=admin_user)
        order_response = client.post("/orders/", json={
            "shipping_address": "Admin Address"
        }, headers=admin_user)
        order_id = order_response.json()["id"]

        # Regular user tries to access admin's order
        response = client.get(f"/orders/my/{order_id}", headers=auth_headers)
        assert response.status_code == 403

    def test_admin_update_order_status(self, client, admin_user, auth_headers, sample_product):
        """Admin can update order status."""
        # Place order as regular user
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)
        order = client.post("/orders/", json={
            "shipping_address": "123 Main St"
        }, headers=auth_headers).json()

        # Admin updates status
        response = client.patch(
            f"/orders/admin/{order['id']}/status",
            json={"status": "confirmed"},
            headers=admin_user
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_regular_user_cannot_update_status(self, client, auth_headers, sample_product):
        """Regular user cannot update order status."""
        # Place order
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)
        order = client.post("/orders/", json={
            "shipping_address": "123 Main St"
        }, headers=auth_headers).json()

        # Try to update status as regular user
        response = client.patch(
            f"/orders/admin/{order['id']}/status",
            json={"status": "confirmed"},
            headers=auth_headers
        )
        assert response.status_code == 403
