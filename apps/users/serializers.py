from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model, with hashed password and role validation."""

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_role(self, value):
        """Validate the role field."""
        valid_roles = [role[0] for role in User.USER_ROLES]  # Assuming USER_ROLES is defined in the model
        if value not in valid_roles:
            raise ValidationError(f"Invalid role. Valid roles are: {', '.join(valid_roles)}.")
        return value

    def create(self, validated_data):
        """Create a user and hash their password."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials and generate tokens."""
        username = data.get('username')
        password = data.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("Invalid username or password.")

        if not user.is_active:
            raise ValidationError("User account is disabled.")

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer to handle password reset request."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if the email exists in the database."""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer to handle password reset confirmation."""

    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data['password_confirm']:
            raise ValidationError("Passwords do not match.")
        return data
