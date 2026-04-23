"""URL routing for the REST API app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LoginView, RegisterView
from .viewsets import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
] + router.urls
