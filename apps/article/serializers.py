from rest_framework import serializers
from .models import Article, Tag, Category,Comment, Like

# class UserSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the User model to get author details.
#     """
#     class Meta:
#         model = User
#         fields = ['id', 'username']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)  # Add author name
    author_email = serializers.EmailField(source='author.email', read_only=True)  # Add author email
    

    class Meta:
        model = Article
        fields = [
            'id', 'author_name', 'author_email', 'title', 'subtitle', 'content', 'status',
            'publish_date', 'categories', 'tags', 'approved_at'
        ]


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    categories = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'content', 'image_url', 'tags',
            'categories', 'publish_date', 'status'
        ]

    def validate_status(self, value):
        request = self.context.get('request')
        if request and not request.user.is_staff and value == 'published':
            raise serializers.ValidationError("Only Admins can directly publish articles.")
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        categories = validated_data.pop('categories', [])
        article = Article.objects.create(**validated_data)

        # Handle tags
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            article.tags.add(tag)

        # Handle categories
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            article.categories.add(category)

        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        categories = validated_data.pop('categories', [])

        # Update the article fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags
        instance.tags.clear()
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)

        # Update categories
        instance.categories.clear()
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            instance.categories.add(category)

        return instance


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'edited')

class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'article', 'author', 'content', 'replies', 'likes_count', 'edited', 'created_at', 'updated_at')
        read_only_fields = ('author', 'likes_count', 'edited', 'created_at', 'updated_at')

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'comment', 'user')
        read_only_fields = ('user',)