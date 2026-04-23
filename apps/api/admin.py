"""Admin registrations for the REST API app."""
from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "is_active", "category", "created_at"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description"]
    list_editable = ["price", "stock", "is_active"]
    ordering = ["-created_at"]
