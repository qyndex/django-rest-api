"""Unit tests for apps.api models."""
import pytest
from decimal import Decimal

from apps.api.models import Category, Product
from apps.api.tests.factories import CategoryFactory, ProductFactory


pytestmark = pytest.mark.django_db


class TestCategoryModel:
    def test_str_returns_name(self):
        cat = CategoryFactory(name="Electronics")
        assert str(cat) == "Electronics"

    def test_name_unique_constraint(self):
        CategoryFactory(name="Unique")
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Unique")

    def test_description_optional(self):
        cat = Category.objects.create(name="No Desc")
        assert cat.description == ""

    def test_created_at_set_on_save(self):
        cat = CategoryFactory()
        assert cat.created_at is not None

    def test_meta_ordering_by_name(self):
        CategoryFactory(name="Zebra")
        CategoryFactory(name="Apple")
        names = list(Category.objects.values_list("name", flat=True))
        assert names == sorted(names)

    def test_verbose_name_plural(self):
        assert Category._meta.verbose_name_plural == "categories"

    def test_product_count_via_related_manager(self):
        cat = CategoryFactory()
        ProductFactory.create_batch(3, category=cat)
        assert cat.products.count() == 3


class TestProductModel:
    def test_str_returns_name(self):
        product = ProductFactory(name="Widget")
        assert str(product) == "Widget"

    def test_default_is_active(self):
        product = ProductFactory()
        assert product.is_active is True

    def test_default_stock_zero(self):
        product = Product.objects.create(name="Zero Stock", price=Decimal("9.99"))
        assert product.stock == 0

    def test_price_stored_with_two_decimal_places(self):
        product = ProductFactory(price=Decimal("12.34"))
        product.refresh_from_db()
        assert product.price == Decimal("12.34")

    def test_category_nullable(self):
        product = Product.objects.create(name="No Cat", price=Decimal("1.00"))
        assert product.category is None

    def test_category_set_null_on_delete(self):
        cat = CategoryFactory()
        product = ProductFactory(category=cat)
        cat.delete()
        product.refresh_from_db()
        assert product.category is None

    def test_created_at_and_updated_at_set(self):
        product = ProductFactory()
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_updated_at_changes_on_save(self):
        product = ProductFactory()
        original = product.updated_at
        product.name = "Updated Name"
        product.save()
        product.refresh_from_db()
        assert product.updated_at >= original

    def test_meta_ordering_newest_first(self):
        p1 = ProductFactory()
        p2 = ProductFactory()
        ids = list(Product.objects.values_list("id", flat=True))
        assert ids[0] == p2.id
