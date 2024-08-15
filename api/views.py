from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Author, Book, Work, Favorite
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from .serializers import AuthorSerializer, BookSerializer, WorkSerializer, FavoriteSerializer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.core.cache import cache


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100 

class AuthorViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]  
    search_fields = ['name']
    def get_permissions(self):
        if self.request.method in ['PUT', 'POST', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super(AuthorViewSet, self).get_permissions()

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]  
    search_fields = ['title']
    def get_permissions(self):
        if self.request.method in ['PUT', 'POST', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super(BookViewSet, self).get_permissions()

class WorkViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    queryset = Work.objects.all()
    serializer_class = WorkSerializer


    
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    permission_classes = [IsAuthenticated]  
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        book = request.data.get('book')
        if Favorite.objects.filter(user=user, book_id=book).exists():
            return Response({'detail': 'Book is already in favorites'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Favorite.objects.filter(user=user).count() >= 20:
            return Response({'detail': 'You can only have 20 favorite books'}, status=status.HTTP_400_BAD_REQUEST)
        
        favorite = Favorite.objects.create(user=user, book_id=book)
        return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):    
        return Response(self.get_user_recommendations(self.request.user))

    def get_user_recommendations(self, user, num_recommendations=5):
        
        favorite_books = Book.objects.filter(favorited_by__user=user).select_related('author')

        if not favorite_books.exists():
            return []
        combined_features = ' '.join(
            [f'{b.title} {b.description} {b.author.name}' for b in favorite_books]
        )
        
        cache_key = f'user_recommendations_{user.id}-{favorite_books.count()}'
        cached_recommendations = cache.get(cache_key)
        if cached_recommendations:
            return cached_recommendations
        similar_books = Book.objects.exclude(favorited_by__user=user).prefetch_related('author')
        all_book_features = []
        all_book_ids = []

        for b in similar_books:
            all_book_features.append(f'{b.title} {b.description} {b.author.name}')
            all_book_ids.append(b.id)

        if not all_book_features:
            return []
        all_book_features.insert(0, combined_features)

        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(all_book_features)

        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        sim_scores = [(index, score) for index, score in enumerate(cosine_sim) if score > 0.0]
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[:num_recommendations]
        indices = [i[0] for i in sim_scores]
        recommended_books = [similar_books[i] for i in indices]

        serialized_recommendations = BookSerializer(recommended_books, many=True).data
        cache.set(cache_key, serialized_recommendations, timeout=60 * 60)
        return serialized_recommendations

    @action(detail=False, methods=['post'])
    def remove(self, request):
        user = request.user
        book_id = request.data.get('book')
        try:
            favorite = Favorite.objects.get(user=user, book_id=book_id)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({'detail': 'Book not found in favorites'}, status=status.HTTP_404_NOT_FOUND)