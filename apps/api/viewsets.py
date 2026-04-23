"""DRF viewsets for the REST API app."""
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductCreateSerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD operations for product categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD operations for products."""

    queryset = Product.objects.select_related("category").all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "stock", "created_at"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProductCreateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        """Set created_by to the authenticated user."""
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="active")
    def active_products(self, request: Request) -> Response:
        """Return only active products."""
        qs = self.get_queryset().filter(is_active=True)
        serializer = ProductSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request: Request) -> Response:
        """Return products with stock below 10."""
        threshold = int(request.query_params.get("threshold", 10))
        qs = self.get_queryset().filter(stock__lt=threshold)
        serializer = ProductSerializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})
