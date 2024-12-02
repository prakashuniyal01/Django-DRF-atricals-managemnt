# serializers.py
import re
import random
from django.core.mail import send_mail
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ValidationError
from .models import User, OTP
from django.contrib.auth.password_validation import validate_password

# User registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'email', 'number', 'full_name', 'role']

    def validate_email(self, value):
        """ Validate email format """
        try:
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
                raise serializers.ValidationError("Invalid email format.")
            return value
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_number(self, value):
        """ Validate phone number format """
        try:
            if not re.match(r"^\+?\d{10,15}$", value):
                raise serializers.ValidationError("Invalid phone number format.")
            return value
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate_password(self, value):
        """ Validate the password against custom rules """
        try:
            # Check password length
            if len(value) < 8 or len(value) > 20:
                raise serializers.ValidationError("Password must be between 8 and 20 characters.")

            # Check for at least one uppercase letter
            if not re.search(r"[A-Z]", value):
                raise serializers.ValidationError("Password must contain at least one uppercase letter.")

            # Check for at least one number
            if not re.search(r"[0-9]", value):
                raise serializers.ValidationError("Password must contain at least one number.")

            # Check for at least one special character
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
                raise serializers.ValidationError("Password must contain at least one special character.")
            
            return value
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def validate(self, data):
        """ Ensure password and confirm_password match """
        try:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"password": "Passwords do not match."})
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        """ Create the user and set `is_active` to False until OTP is verified """
        try:
            validated_data.pop('confirm_password')
            # Set user as inactive initially
            user = User.objects.create_user(
                email=validated_data['email'],
                number=validated_data['number'],
                full_name=validated_data['full_name'],
                role=validated_data['role'],
                is_active=False,  # Inactive by default
            )
            user.set_password(validated_data['password'])
            user.save()

            # Generate and store OTP
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp=otp_code)

            # Send OTP email
            self.send_otp_email(user, otp_code)

            return user

        except ValidationError as e:
            raise serializers.ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Error creating user: {str(e)}")

    def send_otp_email(self, user, otp_code):
        """ Utility function to send OTP via email """
        subject = "Account Verification OTP"
        message = f"Hello {user.full_name},\n\nYour OTP for account verification is: {otp_code}.\nIt is valid for 10 minutes."
        from_email = "maan03saab@gmail.com"  # Replace with your email
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)
        
    def send_account_creation_email(self, user):
        """ Send account creation details via email """
        subject = "Welcome to Our Platform!"
        message = (
            f"Dear {user.full_name},\n\n"
            f"Thank you for registering on our platform.\n"
            f"Here are your account details:\n\n"
            f"Full Name: {user.full_name}\n"
            f"Email: {user.email}\n"
            f"Phone Number: {user.number}\n"
            f"Role: {user.role}\n\n"
            f"Please verify your account using the OTP sent earlier."
        )
        from_email = "maan03saab@gmail.com"  # Replace with your email
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            raise serializers.ValidationError(f"Error sending account creation email: {str(e)}")
        

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            otp_entry = OTP.objects.filter(user=user).last()

            if not otp_entry or otp_entry.otp != data['otp']:
                raise serializers.ValidationError("Invalid or expired OTP.")

            if not otp_entry.is_valid():
                raise serializers.ValidationError("OTP has expired. Please request a new one.")

            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def save(self):
        """ Activate the user after successful OTP validation """
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.is_active = True  # Activate the user
        user.save()

        return user

# User login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            email = attrs.get('email')
            password = attrs.get('password')

            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials", code='authorization')

            attrs['user'] = user
            return attrs
        except Exception as e:
            raise serializers.ValidationError(str(e))

# Update user serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True) 
    class Meta:
        model = User
        fields = ['id','full_name', 'email', 'number','role', 'is_active', 'is_staff']  # Fields you want to allow updates on

    def update(self, instance, validated_data):
        try:
            instance.full_name = validated_data.get('full_name', instance.full_name)
            instance.email = validated_data.get('email', instance.email)
            instance.number = validated_data.get('number', instance.number)
            instance.role = validated_data.get('role', instance.role)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.is_staff = validated_data.get('is_staff', instance.is_staff)

            instance.save()
            return instance
        except DjangoValidationError as e:
            raise serializers.ValidationError(f"Validation Error: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Error updating user: {str(e)}")


# password update 

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": ("New password and confirm password do not match.")})

        # Check if old password is correct
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": ("Old password is incorrect.")})

        # Validate new password against Django's password validators
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return data
    
    
# otp 

class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email.")
        return value


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        from .models import OTP
        try:
            user = User.objects.get(email=data['email'])
            otp_obj = OTP.objects.get(user=user, otp=data['otp'])
            if not otp_obj.is_valid():
                raise serializers.ValidationError("OTP has expired.")
        except (User.DoesNotExist, OTP.DoesNotExist):
            raise serializers.ValidationError("Invalid OTP or email.")
        return data