from rest_framework import serializers
from .models import Author, Work, Book, Favorite


class BookSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'ratings_count', 'average_rating', 'text_reviews_count', 'author']

class NestedBookSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'ratings_count', 'average_rating', 'text_reviews_count', 'author_name', 'author']

class AuthorSerializer(serializers.ModelSerializer):
    books = NestedBookSerializer(many=True, read_only=True)  # List of books by the author

    class Meta:
        model = Author
        fields = ['id', 'name', 'gender', 'image_url', 'about', 'fans_count', 'books']

class WorkSerializer(serializers.ModelSerializer):
    book = NestedBookSerializer(read_only=True)

    class Meta:
        model = Work
        fields = ['id', 'book']


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    book = NestedBookSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id','user', 'book', 'added_at']
