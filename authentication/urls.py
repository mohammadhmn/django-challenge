from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from authentication.views import SignUpView

urlpatterns = [
    path("signin/", ObtainAuthToken.as_view(), name="sign_in"),
    path("signup/", SignUpView.as_view(), name="sign_up"),
]
