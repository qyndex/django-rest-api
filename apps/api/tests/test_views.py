"""Tests for CategoryViewSet and ProductViewSet — search, ordering, custom actions."""
import pytest
from decimal import Decimal

from apps.api.tests.factories import CategoryFactory, ProductFactory


pytestmark = pytest.mark.django_db


class TestCategoryViewSet:
    BASE = "/api/categories/"

    def test_list_returns_200(self, api_client):
        CategoryFactory.create_batch(2)
        res = api_client.get(self.BASE)
        assert res.status_code == 200

    def test_list_envelope_has_results_key(self, api_client):
        CategoryFactory.create_batch(2)
        res = api_client.get(self.BASE)
        data = res.json()
        assert "results" in data or isinstance(data, list)

    def test_list_pagination_count(self, api_client):
        CategoryFactory.create_batch(3)
        res = api_client.get(self.BASE)
        data = res.json()
        # DRF PageNumberPagination wraps in {"count": N, "results": [...]}
        count = data.get("count", len(data))
        assert count >= 3

    def test_retrieve_single_category(self, api_client):
        cat = CategoryFactory(name="Test Cat")
        res = api_client.get(f"{self.BASE}{cat.id}/")
        assert res.status_code == 200
        assert res.json()["name"] == "Test Cat"

    def test_retrieve_nonexistent_returns_404(self, api_client):
        res = api_client.get(f"{self.BASE}999999/")
        assert res.status_code == 404

    def test_create_category(self, api_client):
        payload = {"name": "New Cat", "description": "A description"}
        res = api_client.post(self.BASE, payload, format="json")
        assert res.status_code == 201
        assert res.json()["name"] == "New Cat"

    def test_create_duplicate_name_returns_400(self, api_client):
        CategoryFactory(name="Dup")
        res = api_client.post(self.BASE, {"name": "Dup"}, format="json")
        assert res.status_code == 400

    def test_update_category(self, api_client):
        cat = CategoryFactory(name="Old Name")
        res = api_client.put(
            f"{self.BASE}{cat.id}/",
            {"name": "New Name", "description": ""},
            format="json",
        )
        assert res.status_code == 200
        assert res.json()["name"] == "New Name"

    def test_partial_update_category(self, api_client):
        cat = CategoryFactory(description="old desc")
        res = api_client.patch(
            f"{self.BASE}{cat.id}/",
            {"description": "new desc"},
            format="json",
        )
        assert res.status_code == 200
        assert res.json()["description"] == "new desc"

    def test_delete_category(self, api_client):
        cat = CategoryFactory()
        res = api_client.delete(f"{self.BASE}{cat.id}/")
        assert res.status_code == 204

    def test_search_by_name(self, api_client):
        CategoryFactory(name="Gadgets")
        CategoryFactory(name="Clothing")
        res = api_client.get(f"{self.BASE}?search=Gadget")
        data = res.json()
        results = data.get("results", data)
        assert any("Gadget" in c["name"] for c in results)

    def test_ordering_by_name(self, api_client):
        CategoryFactory(name="Zebra")
        CategoryFactory(name="Aardvark")
        res = api_client.get(f"{self.BASE}?ordering=name")
        data = res.json()
        results = data.get("results", data)
        names = [c["name"] for c in results]
        assert names == sorted(names)

    def test_product_count_field(self, api_client):
        cat = CategoryFactory()
        ProductFactory.create_batch(2, category=cat)
        res = api_client.get(f"{self.BASE}{cat.id}/")
        assert res.json()["product_count"] == 2


class TestProductViewSet:
    BASE = "/api/products/"

    def test_list_returns_200(self, api_client):
        ProductFactory.create_batch(2)
        res = api_client.get(self.BASE)
        assert res.status_code == 200

    def test_create_product(self, api_client):
        cat = CategoryFactory()
        payload = {
            "name": "Widget",
            "description": "A widget",
            "price": "9.99",
            "stock": 100,
            "is_active": True,
            "category": cat.id,
        }
        res = api_client.post(self.BASE, payload, format="json")
        assert res.status_code == 201
        assert res.json()["name"] == "Widget"

    def test_create_product_without_category(self, api_client):
        payload = {"name": "Standalone", "price": "1.00", "stock": 5}
        res = api_client.post(self.BASE, payload, format="json")
        assert res.status_code == 201

    def test_create_product_negative_price_rejected(self, api_client):
        payload = {"name": "Bad Price", "price": "-1.00", "stock": 0}
        res = api_client.post(self.BASE, payload, format="json")
        assert res.status_code == 400

    def test_retrieve_product(self, api_client):
        product = ProductFactory(name="My Product")
        res = api_client.get(f"{self.BASE}{product.id}/")
        assert res.status_code == 200
        assert res.json()["name"] == "My Product"

    def test_retrieve_includes_category_name(self, api_client):
        cat = CategoryFactory(name="Electronics")
        product = ProductFactory(category=cat)
        res = api_client.get(f"{self.BASE}{product.id}/")
        assert res.json()["category_name"] == "Electronics"

    def test_update_product(self, api_client):
        product = ProductFactory()
        payload = {
            "name": "Updated",
            "price": "19.99",
            "stock": 50,
            "is_active": True,
        }
        res = api_client.put(f"{self.BASE}{product.id}/", payload, format="json")
        assert res.status_code == 200
        assert res.json()["name"] == "Updated"

    def test_partial_update_stock(self, api_client):
        product = ProductFactory(stock=10)
        res = api_client.patch(
            f"{self.BASE}{product.id}/", {"stock": 99}, format="json"
        )
        assert res.status_code == 200

    def test_delete_product(self, api_client):
        product = ProductFactory()
        res = api_client.delete(f"{self.BASE}{product.id}/")
        assert res.status_code == 204

    def test_search_by_name(self, api_client):
        ProductFactory(name="Blue Widget")
        ProductFactory(name="Red Gadget")
        res = api_client.get(f"{self.BASE}?search=Widget")
        data = res.json()
        results = data.get("results", data)
        assert all("Widget" in p["name"] for p in results)

    def test_ordering_by_price_ascending(self, api_client):
        ProductFactory(price=Decimal("5.00"))
        ProductFactory(price=Decimal("20.00"))
        ProductFactory(price=Decimal("1.00"))
        res = api_client.get(f"{self.BASE}?ordering=price")
        data = res.json()
        results = data.get("results", data)
        prices = [Decimal(p["price"]) for p in results]
        assert prices == sorted(prices)

    def test_active_products_action(self, api_client):
        ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        res = api_client.get(f"{self.BASE}active/")
        assert res.status_code == 200
        data = res.json()
        results = data if isinstance(data, list) else data.get("results", data)
        assert all(p["is_active"] for p in results)

    def test_low_stock_action_default_threshold(self, api_client):
        ProductFactory(stock=5)
        ProductFactory(stock=100)
        res = api_client.get(f"{self.BASE}low-stock/")
        assert res.status_code == 200
        data = res.json()
        assert "count" in data
        assert "results" in data
        assert data["count"] >= 1
        for p in data["results"]:
            assert p["stock"] < 10

    def test_low_stock_action_custom_threshold(self, api_client):
        ProductFactory(stock=50)
        ProductFactory(stock=200)
        res = api_client.get(f"{self.BASE}low-stock/?threshold=100")
        assert res.status_code == 200
        data = res.json()
        for p in data["results"]:
            assert p["stock"] < 100
