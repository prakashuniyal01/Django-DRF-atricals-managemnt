from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .serializers import (
    UserSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

User = get_user_model()

# user registers 
class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create method to handle custom user registration logic (if any).
        """
        return super().create(request, *args, **kwargs)


class LoginView(APIView):
    """
    Login view for user authentication.
    Returns JWT access and refresh tokens along with user details.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract credentials from validated data
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid username or password")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Prepare response
        response_data = {
            "message": "Login successful",
            "refresh": str(refresh),  # Refresh token
            "access": access_token,  # Access token
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UserListCreate(generics.ListCreateAPIView):
    """
    View for listing all users and creating a new user.
    Only accessible by admins.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class UserDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a user.
    Accessible only by authenticated users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PasswordResetRequestView(APIView):
    """
    Sends a password reset email with a tokenized link.
    """
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("No user found with this email address.")

        # Generate password reset token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.id).encode())

        # Construct reset link
        reset_url = f"http://{get_current_site(request).domain}/reset-password/{uid}/{token}/"

        # Send reset email
        send_mail(
            subject="Password Reset Request",
            message=f"To reset your password, click the following link: {reset_url}",
            from_email="no-reply@yourdomain.com",
            recipient_list=[email],
        )

        return Response(
            {"message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Confirms password reset and sets a new password.
    """
    def post(self, request, uidb64, token):
        try:
            # Decode UID and retrieve user
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError("Invalid or expired reset link.")

        # Validate the token
        if not default_token_generator.check_token(user, token):
            raise ValidationError("Invalid or expired token.")

        # Validate and set the new password
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['password'])
        user.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )