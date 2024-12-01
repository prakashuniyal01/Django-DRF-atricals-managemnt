from django.urls import path
from .views import OTPVerificationView, UserRegisterView, LoginView, UserUpdateView,PasswordChangeView,SendOtpView, VerifyOtpView, ResendOTPView
from django.views.generic import TemplateView


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('register-verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:user_id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    
    # pages rendering 
    path('login-page/', TemplateView.as_view(template_name='login.html'), name='login'),  # Login HTML Page
    path('register-page/', TemplateView.as_view(template_name='register.html'), name='register'),  # Register HTML Page
    path('forgot-password-page/', TemplateView.as_view(template_name='forgot_password.html'), name='forgot-password'),  # Forgot Password HTML Page
    # path('change-password-page/', TemplateView.as_view(template_name='change_password.html'), name='change-password'),  # Change Password HTML Page
    path('verify-otp-page/', TemplateView.as_view(template_name='verify_otp.html'), name='verify-otp'),  # Verify OTP HTML Page
    path('resend-otp-page/', TemplateView.as_view(template_name='resend_otp.html'), name='resend-otp'),  # Resend OTP HTML Page
]
