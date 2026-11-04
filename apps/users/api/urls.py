from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.api.views import LoginView

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
