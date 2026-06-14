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
    path('booking/my/', views.UserBookingView.as_view(), name='my-bookings'),
    path('booking/cancel/', views.BookingCancelView.as_view(), name='booking-cancel'),
    path('booking/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('booking/status/', views.BookingAcceptView.as_view(), name='booking-accept'),
    path('booking/payment/verify/', views.BookingPaymentVerifyView.as_view(), name='booking-payment-verify'),
    path('booking/payment/callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    path('token/', views.LogInView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/google/', views.GoogleAuthView.as_view(), name='google-auth'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/password-reset/validate-token/', views.PasswordResetValidateTokenView.as_view(), name='password-reset-validate-token'),
]
