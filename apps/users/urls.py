from django.urls import path
from .views import (
    UserRegistrationView, 
    UserListCreate, 
    UserDetailUpdateDelete,
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    LoginView
)

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='user-register'),
    path('login', LoginView.as_view(), name='login'),
    path('users', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:pk>', UserDetailUpdateDelete.as_view(), name='user-detail-update-delete'),
    path('reset-password', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
