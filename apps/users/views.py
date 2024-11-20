# views.py
import random
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from datetime import timedelta  
from django.utils.timezone import now
from django.conf import settings
from .models import User,OTP
from .serializers import UserRegistrationSerializer, LoginSerializer, UserUpdateSerializer,PasswordChangeSerializer,SendOtpSerializer, VerifyOtpSerializer
from django.utils.translation import gettext_lazy as _


# user registration view
class UserRegisterView(APIView):
   def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# user login views
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Check if the user is already logged in
            if request.user and request.user.is_authenticated:
                user = request.user
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Prepare user data
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'number': user.number,
                }

                return Response({
                    'user': user_data,
                    'refresh': str(refresh),
                    'access': access_token,
                }, status=status.HTTP_200_OK)

            # If the user is not logged in, proceed with normal login process
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Prepare user data
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'number': user.number,
                }

                return Response({
                    'user': user_data,
                    'refresh': str(refresh),
                    'access': access_token,
                }, status=status.HTTP_200_OK)

            # If the data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# user update and patch view
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None

    def patch(self, request, user_id, *args, **kwargs):
        try:
            # Only authenticated users can access this view
            user = self.get_object(user_id)
            if not user:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Ensure the logged-in user can only update their own details or the admin
            if request.user != user and not request.user.is_superuser:
                return Response({"detail": "You are not authorized to update this user's details."}, status=status.HTTP_403_FORBIDDEN)

            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, user_id, *args, **kwargs):
        try:
            # Only authenticated users can access this view
            user = self.get_object(user_id)
            if not user:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Ensure the logged-in user can only update their own details or the admin
            if request.user != user and not request.user.is_superuser:
                return Response({"detail": "You are not authorized to update this user's details."}, status=status.HTTP_403_FORBIDDEN)

            serializer = UserUpdateSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# change password 
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Create and validate the serializer
            serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                # Get the new password from validated data
                new_password = serializer.validated_data['new_password']

                # Update the password for the authenticated user
                user = request.user
                user.set_password(new_password)
                user.save()

                return Response({"message": _("Password updated successfully.")}, status=status.HTTP_200_OK)
            
            # If validation fails, return errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except DRFValidationError as e:
            # Handle DRF validation errors (custom exceptions)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except DjangoValidationError as e:
            # Handle any Django validation errors
            return Response({"detail": _("Validation error: ") + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Catch any unexpected errors
            return Response({"detail": _("An unexpected error occurred. Please try again.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# send otps  
class SendOtpView(APIView):
    def post(self, request):
        serializer = SendOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp=otp)

            # Send OTP via email
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}",
                from_email="your-email@gmail.com",
                recipient_list=[email],
            )
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']

            # Update user password
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Clean up OTP
            OTP.objects.filter(user=user).delete()

            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# resend otp
class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ensure the user exists
            user = User.objects.get(email=email)

            # Check if an OTP already exists for the user
            otp_record = OTP.objects.filter(user=user).order_by('-created_at').first()

            if otp_record and otp_record.created_at > now() - timedelta(minutes=2):
                time_remaining = 120 - int((now() - otp_record.created_at).total_seconds())
                return Response(
                    {"detail": f"Please wait {time_remaining} seconds before requesting a new OTP."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Generate a new OTP using random
            new_otp = str(random.randint(100000, 999999))  # Generate a 6-digit random OTP

            # Save the new OTP in the database
            OTP.objects.create(user=user, otp=new_otp)

            # Send the OTP via email
            send_mail(
                subject="Your OTP for Password Reset",
                message=f"Your OTP is {new_otp}. It is valid for 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response({"detail": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"detail": "An error occurred while processing your request.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )