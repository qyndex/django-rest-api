"""DRF serializers for the REST API app."""
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    product_count = serializers.IntegerField(
        source="products.count",
        read_only=True,
    )

    class Meta:
        model = Category
        fields = ["id", "name", "description", "product_count", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "is_active",
            "category",
            "category_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating a Product."""

    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "is_active", "category"]

    def validate_price(self, value: float) -> float:
        if value < 0:
            raise serializers.ValidationError("Price must be non-negative.")
        return value
