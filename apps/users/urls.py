from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import OTPVerificationView, UserRegisterView, LoginView, UserUpdateView, PasswordChangeView, SendOtpView, VerifyOtpView, ResendOTPView, UserDetailView, AdminUserView
from django.views.generic import TemplateView

urlpatterns = [
    # User-related views
    path('register/', UserRegisterView.as_view(), name='register'),
    path('register-verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('user/<int:user_id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    
    # OTP-related views
    path('forget-otp/', SendOtpView.as_view(), name='forget-otp'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),

    # Login and JWT authentication views
    path('login/', LoginView.as_view(), name='login'),  # Custom LoginView (if you have custom logic)
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT login using TokenObtainPairView
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT token refresh

    # Page rendering views
    path('login-page/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register-page/', TemplateView.as_view(template_name='register.html'), name='register'),
    
    path('dashboard/admin/', TemplateView.as_view(template_name='dashboard/admin.html'),  name='user-detail'),
    path('dashboard/editor/', TemplateView.as_view(template_name='dashboard/editor.html'), name='dashboard-editor'),
    path('dashboard/journalist/', TemplateView.as_view(template_name='dashboard/journalist.html'),  name='user-detail'),
    
    # Make sure this path is correct for user dashboard
    path('dashboard/user/', TemplateView.as_view(template_name='dashboard/user.html'), name='user-detail'),

    # Add the following to handle /user/dashboard/
    # path('user/dashboard/', TemplateView.as_view(template_name='dashboard/user.html'), name='user-detail'),
    
    # admins crud should
    path('admin/users/', AdminUserView.as_view(), name='admin-users-list'),  # For listing users
    path('admin/users/<int:user_id>/', AdminUserView.as_view(), name='admin-user-detail'),  # For updating, deleting, or changing password for a user
    # path('admin/users/<int:user_id>/change-password/', ChangePasswordView.as_view(), name='change-password'),
]