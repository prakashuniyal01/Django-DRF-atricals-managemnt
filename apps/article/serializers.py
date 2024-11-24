from rest_framework import serializers
from .models import Article, Tag, Category


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)  # Serialize tags with their names
    categories = CategorySerializer(many=True, read_only=True)  # Serialize categories with their names

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'subtitle', 'content', 'status', 
            'publish_date', 'categories', 'tags', 'approved_at'
        ]


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)  # Allow tag IDs for creation
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)  # Allow category IDs for creation

    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'content', 'image_url', 'tags', 
            'categories', 'publish_date', 'status'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def validate_status(self, value):
        request = self.context.get('request')
        if request and not request.user.is_staff and value == 'published':
            raise serializers.ValidationError("Only Admins can directly publish articles.")
        return value
