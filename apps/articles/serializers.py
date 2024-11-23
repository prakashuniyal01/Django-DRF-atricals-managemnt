from rest_framework import serializers
from .models import Article
import cloudinary.uploader
from datetime import date

class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)  # Accept image upload
    image_url = serializers.URLField(read_only=True)  # Output Cloudinary URL
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = Article
        fields = [
            "id", "title", "subtitle", "content", "author", "author_email",
            "image_url", "tags", "category", "publish_date", "status",
            "created_at", "updated_at"
        ]
        read_only_fields = ['id', 'status', 'image_url', 'author']  # Mark 'author' as read-only

    def validate_title(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("The title must be at least 10 characters long.")
        return value

    def validate_publish_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError("The publish date must be a future date.")
        return value

    def create(self, validated_data):
        # Handle Cloudinary upload for the image
        image = validated_data.pop('image', None)  # Remove image field from validated_data
        if image:
            # Upload the image to Cloudinary
            upload_result = cloudinary.uploader.upload(image)
            validated_data['image_url'] = upload_result['url']  # Set the image URL returned by Cloudinary
        
        # Create the Article instance
        article = super().create(validated_data)
        return article

    def update(self, instance, validated_data):
        # Handle image updates
        image = validated_data.pop('image', None)  # Remove image field from validated_data
        if image:
            # Upload the new image to Cloudinary
            upload_result = cloudinary.uploader.upload(image)
            validated_data['image_url'] = upload_result['url']  # Update image URL
        
        # Update the instance with validated data
        return super().update(instance, validated_data)
