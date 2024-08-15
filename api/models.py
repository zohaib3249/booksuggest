from django.db import models
from accounts.models import Users

class Author(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # Assuming 'id' is a string
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    fans_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=255, null=True,blank=True)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    work_id = models.CharField(max_length=50, null=True,blank=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    isbn13 = models.CharField(max_length=17, blank=True, null=True)
    language = models.CharField(max_length=10, default="en")
    average_rating = models.FloatField(default=0.0)
    ratings_count = models.IntegerField(default=0)
    text_reviews_count = models.IntegerField(default=0)
    publication_date = models.CharField(max_length=20,null=True,blank=True)
    original_publication_date = models.CharField(max_length=20, null=True,blank=True)
    format = models.CharField(max_length=50, blank=True, null=True)
    edition_information = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    num_pages = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    

class Work(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    book = models.ForeignKey(Book, related_name='works', on_delete=models.CASCADE)

    def __str__(self):
        return self.id
    
class Favorite(models.Model):
    user = models.ForeignKey(Users, related_name='favorites', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorited_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.first_name} - {self.book.title}'