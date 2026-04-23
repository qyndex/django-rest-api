"""Integration-style API tests covering serializer fields, validation, and URL routing."""
import pytest
from decimal import Decimal

from apps.api.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductCreateSerializer,
)
from apps.api.tests.factories import CategoryFactory, ProductFactory


pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Serializer unit tests
# ---------------------------------------------------------------------------


class TestCategorySerializer:
    def test_serializes_expected_fields(self):
        cat = CategoryFactory()
        data = CategorySerializer(cat).data
        assert set(data.keys()) >= {"id", "name", "description", "product_count", "created_at"}

    def test_read_only_fields_not_writable(self):
        serializer = CategorySerializer(
            data={"id": 999, "name": "Forced ID", "created_at": "2000-01-01T00:00:00Z"}
        )
        assert serializer.is_valid()
        # id and created_at should be stripped from validated_data
        assert "id" not in serializer.validated_data
        assert "created_at" not in serializer.validated_data

    def test_name_required(self):
        serializer = CategorySerializer(data={"description": "no name"})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_product_count_is_integer(self):
        cat = CategoryFactory()
        ProductFactory.create_batch(2, category=cat)
        data = CategorySerializer(cat).data
        assert data["product_count"] == 2


class TestProductSerializer:
    def test_serializes_expected_fields(self):
        product = ProductFactory()
        data = ProductSerializer(product).data
        assert set(data.keys()) >= {
            "id", "name", "description", "price", "stock",
            "is_active", "category", "category_name", "created_by",
            "created_at", "updated_at",
        }

    def test_category_name_from_related(self):
        cat = CategoryFactory(name="Tools")
        product = ProductFactory(category=cat)
        data = ProductSerializer(product).data
        assert data["category_name"] == "Tools"

    def test_category_name_none_if_no_category(self):
        product = ProductFactory(category=None)
        data = ProductSerializer(product).data
        assert data["category_name"] is None

    def test_read_only_timestamps(self):
        serializer = ProductSerializer(
            data={
                "name": "X",
                "price": "1.00",
                "stock": 1,
                "created_at": "2000-01-01T00:00:00Z",
            }
        )
        assert serializer.is_valid()
        assert "created_at" not in serializer.validated_data

    def test_created_by_is_read_only(self):
        serializer = ProductSerializer(
            data={
                "name": "X",
                "price": "1.00",
                "stock": 1,
                "created_by": 999,
            }
        )
        assert serializer.is_valid()
        assert "created_by" not in serializer.validated_data


class TestProductCreateSerializer:
    def test_valid_data_passes(self):
        cat = CategoryFactory()
        serializer = ProductCreateSerializer(
            data={"name": "Item", "price": "10.00", "stock": 5, "category": cat.id}
        )
        assert serializer.is_valid(), serializer.errors

    def test_negative_price_rejected(self):
        serializer = ProductCreateSerializer(
            data={"name": "Bad", "price": "-0.01", "stock": 0}
        )
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_zero_price_accepted(self):
        serializer = ProductCreateSerializer(
            data={"name": "Free Item", "price": "0.00", "stock": 0}
        )
        assert serializer.is_valid(), serializer.errors

    def test_name_required(self):
        serializer = ProductCreateSerializer(data={"price": "1.00"})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_price_required(self):
        serializer = ProductCreateSerializer(data={"name": "No Price"})
        assert not serializer.is_valid()
        assert "price" in serializer.errors


# ---------------------------------------------------------------------------
# URL routing / router registration
# ---------------------------------------------------------------------------


class TestURLRouting:
    def test_categories_list_url_resolves(self, api_client):
        res = api_client.get("/api/categories/")
        assert res.status_code in (200, 401, 403)

    def test_products_list_url_resolves(self, api_client):
        res = api_client.get("/api/products/")
        assert res.status_code in (200, 401, 403)

    def test_categories_detail_url_resolves(self, api_client):
        cat = CategoryFactory()
        res = api_client.get(f"/api/categories/{cat.id}/")
        assert res.status_code == 200

    def test_products_active_action_url_resolves(self, api_client):
        res = api_client.get("/api/products/active/")
        assert res.status_code in (200, 401, 403)

    def test_products_low_stock_action_url_resolves(self, api_client):
        res = api_client.get("/api/products/low-stock/")
        assert res.status_code in (200, 401, 403)

    def test_auth_register_url_resolves(self, api_client):
        res = api_client.post(
            "/api/auth/register/",
            {"username": "route_test", "password": "testpass123"},
            format="json",
        )
        assert res.status_code == 201

    def test_auth_login_url_resolves(self, api_client):
        res = api_client.post(
            "/api/auth/login/",
            {"username": "nobody", "password": "wrong"},
            format="json",
        )
        assert res.status_code == 401


# ---------------------------------------------------------------------------
# End-to-end lifecycle: create -> read -> update -> delete
# ---------------------------------------------------------------------------


class TestProductLifecycle:
    def test_full_crud_lifecycle(self, auth_client):
        cat = CategoryFactory()

        # Create
        create_res = auth_client.post(
            "/api/products/",
            {"name": "Lifecycle Widget", "price": "29.99", "stock": 10, "category": cat.id},
            format="json",
        )
        assert create_res.status_code == 201
        product_id = create_res.json()["id"]

        # Read
        read_res = auth_client.get(f"/api/products/{product_id}/")
        assert read_res.status_code == 200
        assert read_res.json()["name"] == "Lifecycle Widget"

        # Update
        update_res = auth_client.patch(
            f"/api/products/{product_id}/",
            {"stock": 0, "is_active": False},
            format="json",
        )
        assert update_res.status_code == 200

        # Confirm no longer in active list
        active_res = auth_client.get("/api/products/active/")
        active_ids = [p["id"] for p in active_res.json()]
        assert product_id not in active_ids

        # Confirm appears in low-stock with threshold=1
        low_res = auth_client.get("/api/products/low-stock/?threshold=1")
        low_ids = [p["id"] for p in low_res.json()["results"]]
        assert product_id in low_ids

        # Delete
        delete_res = auth_client.delete(f"/api/products/{product_id}/")
        assert delete_res.status_code == 204

        # Confirm 404 after delete
        gone_res = auth_client.get(f"/api/products/{product_id}/")
        assert gone_res.status_code == 404


class TestCategoryWithProducts:
    def test_deleting_category_nullifies_product_category(self, auth_client):
        cat = CategoryFactory()
        product = ProductFactory(category=cat)

        auth_client.delete(f"/api/categories/{cat.id}/")

        read_res = auth_client.get(f"/api/products/{product.id}/")
        assert read_res.status_code == 200
        assert read_res.json()["category"] is None
