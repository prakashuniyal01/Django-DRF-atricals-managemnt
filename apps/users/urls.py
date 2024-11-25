from django.urls import path
from .views import OTPVerificationView, UserRegisterView, LoginView, UserUpdateView,PasswordChangeView,SendOtpView, VerifyOtpView, ResendOTPView



urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('register-verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
]
