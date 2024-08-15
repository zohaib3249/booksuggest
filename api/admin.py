from django.contrib import admin

from api.models import *
# Register your models here.
admin.site.register([Author, Work, Book, Favorite, Users])