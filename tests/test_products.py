import pytest


class TestGetProducts:
    """Tests for GET /products/"""

    def test_get_products_empty(self, client):
        """Returns empty list when no products."""
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert isinstance(data["items"], list)

    def test_get_products_with_data(self, client, sample_product):
        """Returns products list."""
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_get_products_pagination(self, client, sample_product):
        """Pagination params work correctly."""
        response = client.get("/products/?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5

    def test_get_products_search(self, client, sample_product):
        """Search by name works."""
        response = client.get("/products/?search=iPhone")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any("iPhone" in item["name"] for item in data["items"])

    def test_get_products_search_no_results(self, client, sample_product):
        """Search with no matches returns empty."""
        response = client.get("/products/?search=XYZNOTEXIST")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_get_products_filter_by_category(self, client, sample_product):
        """Filter by category_id works."""
        response = client.get(f"/products/?category_id={sample_product['category_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_get_products_public_no_auth(self, client, sample_product):
        """Product listing is public — no token needed."""
        response = client.get("/products/")
        assert response.status_code == 200


class TestGetProduct:
    """Tests for GET /products/{id}"""

    def test_get_product_success(self, client, sample_product):
        """Get existing product by ID."""
        response = client.get(f"/products/{sample_product['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_product["id"]
        assert data["name"] == sample_product["name"]

    def test_get_product_not_found(self, client):
        """Non-existent product returns 404."""
        response = client.get("/products/99999")
        assert response.status_code == 404
        assert response.json()["error"]["type"] == "NOT_FOUND"


class TestCreateProduct:
    """Tests for POST /products/"""

    def test_create_product_success(self, client, admin_user, sample_category):
        """Admin can create product."""
        response = client.post("/products/", json={
            "name": "Samsung S24",
            "price": 69999.0,
            "stock": 5,
            "category_id": sample_category["id"],
            "description": "Samsung flagship"
        }, headers=admin_user)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Samsung S24"
        assert data["price"] == 69999.0
        assert data["is_available"] == True

    def test_create_product_without_auth(self, client, sample_category):
        """Cannot create product without token."""
        response = client.post("/products/", json={
            "name": "Test Phone",
            "price": 9999.0,
            "stock": 5,
            "category_id": sample_category["id"]
        })
        assert response.status_code == 401

    def test_create_product_invalid_price(self, client, auth_headers, sample_category):
        """Negative price should fail validation."""
        response = client.post("/products/", json={
            "name": "Cheap Phone",
            "price": -100.0,   # invalid!
            "stock": 5,
            "category_id": sample_category["id"]
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_product_zero_stock_not_available(self, client, admin_user, sample_category):
        """Product with 0 stock should have is_available=False."""
        response = client.post("/products/", json={
            "name": "Out of Stock Item",
            "price": 999.0,
            "stock": 0,
            "category_id": sample_category["id"]
        }, headers=admin_user)
        assert response.status_code == 201
        assert response.json()["is_available"] == False

    def test_create_product_invalid_category(self, client, admin_user):
        """Non-existent category_id returns 404."""
        response = client.post("/products/", json={
            "name": "Some Product",
            "price": 999.0,
            "stock": 5,
            "category_id": 99999
        }, headers=admin_user)
        assert response.status_code == 404


class TestUpdateProduct:
    """Tests for PATCH /products/{id}"""

    def test_update_price(self, client, auth_headers, sample_product):
        """Update only price — other fields unchanged."""
        response = client.patch(
            f"/products/{sample_product['id']}",
            json={"price": 74999.0},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 74999.0
        assert data["name"] == sample_product["name"]  # unchanged

    def test_update_without_auth(self, client, sample_product):
        """Cannot update without token."""
        response = client.patch(
            f"/products/{sample_product['id']}",
            json={"price": 100.0}
        )
        assert response.status_code == 401

    def test_update_stock_updates_availability(self, client, auth_headers, sample_product):
        """Setting stock to 0 makes product unavailable."""
        response = client.patch(
            f"/products/{sample_product['id']}",
            json={"stock": 0},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["is_available"] == False


class TestDeleteProduct:
    """Tests for DELETE /products/{id}"""

    def test_delete_requires_admin(self, client, auth_headers, sample_product):
        """Regular user cannot delete product."""
        response = client.delete(
            f"/products/{sample_product['id']}",
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_delete_success(self, client, admin_user, sample_product):
        """Admin can delete product."""
        response = client.delete(
            f"/products/{sample_product['id']}",
            headers=admin_user
        )
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/products/{sample_product['id']}")
        assert get_response.status_code == 404
