import pytest


class TestCart:
    """Tests for cart endpoints."""

    def test_get_empty_cart(self, client, auth_headers):
        """New user gets empty cart."""
        response = client.get("/cart/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_amount"] == 0.0
        assert data["total_items"] == 0

    def test_get_cart_requires_auth(self, client):
        """Cart requires authentication."""
        response = client.get("/cart/")
        assert response.status_code == 401

    def test_add_to_cart(self, client, auth_headers, sample_product):
        """Add product to cart."""
        response = client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 2
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["total_items"] == 2

    def test_add_same_product_increases_quantity(self, client, auth_headers, sample_product):
        """Adding same product again increases quantity."""
        # Add once
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)

        # Add again
        response = client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 2
        }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["quantity"] == 3  # 1 + 2

    def test_add_invalid_product(self, client, auth_headers):
        """Cannot add non-existent product."""
        response = client.post("/cart/items", json={
            "product_id": 99999,
            "quantity": 1
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_cart_total_calculated_correctly(self, client, auth_headers, sample_product):
        """Total amount = price * quantity."""
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 2
        }, headers=auth_headers)

        response = client.get("/cart/", headers=auth_headers)
        data = response.json()
        expected_total = sample_product["price"] * 2
        assert data["total_amount"] == round(expected_total, 2)

    def test_remove_cart_item(self, client, auth_headers, sample_product):
        """Remove item from cart."""
        # Add item
        add_response = client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)
        item_id = add_response.json()["items"][0]["id"]

        # Remove it
        response = client.delete(f"/cart/items/{item_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["items"] == []

    def test_clear_cart(self, client, auth_headers, sample_product):
        """Clear entire cart."""
        # Add item
        client.post("/cart/items", json={
            "product_id": sample_product["id"],
            "quantity": 1
        }, headers=auth_headers)

        # Clear
        response = client.delete("/cart/", headers=auth_headers)
        assert response.status_code == 204

        # Verify empty
        cart = client.get("/cart/", headers=auth_headers)
        assert cart.json()["items"] == []
