"""Management command to seed the database with sample data."""
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.api.models import Category, Product


class Command(BaseCommand):
    help = "Seed database with sample categories and products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing data."))

        categories_data = [
            {"name": "Electronics", "description": "Electronic devices and accessories"},
            {"name": "Clothing", "description": "Apparel and fashion items"},
            {"name": "Home & Garden", "description": "Home improvement and garden supplies"},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]},
            )
            categories[cat.name] = cat
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {status}: Category '{cat.name}'")

        products_data = [
            {"name": "Wireless Headphones", "price": Decimal("79.99"), "stock": 150, "category": "Electronics"},
            {"name": "USB-C Hub", "price": Decimal("34.99"), "stock": 200, "category": "Electronics"},
            {"name": "Mechanical Keyboard", "price": Decimal("129.99"), "stock": 75, "category": "Electronics"},
            {"name": "4K Monitor", "price": Decimal("449.99"), "stock": 30, "category": "Electronics"},
            {"name": "Cotton T-Shirt", "price": Decimal("19.99"), "stock": 500, "category": "Clothing"},
            {"name": "Denim Jacket", "price": Decimal("89.99"), "stock": 60, "category": "Clothing"},
            {"name": "Running Shoes", "price": Decimal("119.99"), "stock": 120, "category": "Clothing"},
            {"name": "Garden Hose (50ft)", "price": Decimal("29.99"), "stock": 80, "category": "Home & Garden"},
            {"name": "LED Desk Lamp", "price": Decimal("44.99"), "stock": 200, "category": "Home & Garden"},
            {"name": "Tool Set (52-piece)", "price": Decimal("64.99"), "stock": 45, "category": "Home & Garden"},
        ]

        for prod_data in products_data:
            category = categories.get(prod_data["category"])
            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "price": prod_data["price"],
                    "stock": prod_data["stock"],
                    "category": category,
                    "description": f"Sample {prod_data['name'].lower()}",
                },
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {status}: Product '{product.name}'")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {Category.objects.count()} categories, "
                f"{Product.objects.count()} products in database."
            )
        )
