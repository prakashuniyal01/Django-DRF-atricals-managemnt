# views.py
import random
from django.core.mail import send_mail
from rest_framework import  status
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
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, LoginSerializer, UserUpdateSerializer,PasswordChangeSerializer,SendOtpSerializer, VerifyOtpSerializer
from django.utils.translation import gettext_lazy as _
import logging


logger = logging.getLogger(__name__)

# Admin User CRUD Operations View
class AdminUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """ Get user(s) details - Admin only """
        if not request.user.is_superuser:
            return Response({"detail": "You are not authorized to view this information."}, status=status.HTTP_403_FORBIDDEN)

        try:
            if user_id:
                # Fetch a single user's details
                user = User.objects.get(id=user_id)
                serializer = UserUpdateSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Fetch all users
                users = User.objects.all()
                serializer = UserUpdateSerializer(users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        """ Create a new user - Admin only """
        if not request.user.is_superuser:
            return Response({"detail": "You are not authorized to create a user."}, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({"message": "User created successfully.", "user": serializer.data}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, user_id):
        """ Update a user's details - Admin only """
        if not request.user.is_superuser:
            return Response({"detail": "You are not authorized to update this user's details."}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        """ Partially update a user's details - Admin only """
        if not request.user.is_superuser:
            return Response({"detail": "You are not authorized to update this user's details."}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        """ Delete a user - Admin only """
        if not request.user.is_superuser:
            return Response({"detail": "You are not authorized to delete this user."}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"detail": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Retrieve the current user's details """
        user = request.user
        serializer = UserUpdateSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """ Update the current user's details """
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        
        
class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Save the validated data and activate the user
                user = serializer.save()

                logger.info(f"User {user.email} successfully verified their account.")
                return Response(
                    {"message": "Account verified successfully.", "user": user.email},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                logger.error(f"Unexpected error during OTP verification for {request.data.get('email')}: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # If serializer is not valid, return errors
        logger.warning(f"OTP verification failed for {request.data.get('email')}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
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
            try:
                user = User.objects.get(email=email)

                # Check for an existing OTP
                otp_record = OTP.objects.filter(user=user).order_by('-created_at').first()

                if otp_record and otp_record.created_at > now() - timedelta(minutes=10):
                    time_remaining = 600 - int((now() - otp_record.created_at).total_seconds())
                    return Response(
                        {
                            "detail": f"OTP has already been sent. Please wait {time_remaining} seconds before requesting a new OTP."
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                # Generate new OTP
                otp = str(random.randint(100000, 999999))
                OTP.objects.create(user=user, otp=otp)

                # Send OTP via email
                send_mail(
                    subject="Password Reset OTP",
                    message=f"Your OTP for password reset is: {otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

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
            user = User.objects.get(email=email)

            # Check if an OTP already exists for the user
            otp_record = OTP.objects.filter(user=user).order_by('-created_at').first()

            if otp_record and otp_record.created_at > now() - timedelta(minutes=1.5):
                time_remaining = 90 - int((now() - otp_record.created_at).total_seconds())
                return Response(
                    {"detail": f"Please wait {time_remaining} seconds before requesting a new OTP."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Generate new OTP
            new_otp = str(random.randint(100000, 999999))

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
 