from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView
)

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('users/', views.UserView.as_view(), name='user'),
    path('users/me/', views.UserMeView.as_view(), name='user-me'),
    path('amenities/', views.AmentiesView.as_view(), name='amenties'),
    path('properties/', views.PropertyView.as_view(), name='property'),
    path('properties/create/', views.PropertyCreateView.as_view(), name='property-create'),
    path('properties/update/<str:id>/', views.PropertyCreateView.as_view(), name='property-update'),
    path('booking/', views.BookingView.as_view(), name='booking'),
    path('token/', views.LogInView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]