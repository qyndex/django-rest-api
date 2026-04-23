"""factory-boy factories for the api app models."""
import factory
from factory.django import DjangoModelFactory

from apps.api.models import Category, Product


class CategoryFactory(DjangoModelFactory):
    """Factory for Category model."""

    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker("sentence")

    class Meta:
        model = Category
        # Avoids IntegrityError on repeated calls within the same test.
        django_get_or_create = ("name",)


class ProductFactory(DjangoModelFactory):
    """Factory for Product model."""

    name = factory.Sequence(lambda n: f"Product {n}")
    description = factory.Faker("paragraph")
    price = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=1,
        max_value=9999,
    )
    stock = factory.Faker("random_int", min=0, max=500)
    is_active = True
    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = Product
