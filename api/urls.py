from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'books', views.BookViewSet)
router.register(r'works', views.WorkViewSet)
router.register(r'favorites', views.FavoriteViewSet, basename='favorites')



urlpatterns =[
        path('/', include(router.urls)),

]