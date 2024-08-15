import json
from django.core.management.base import BaseCommand
from api.models import Author, Book

class Command(BaseCommand):
    help = 'Import the top 100,000 books data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file to import')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        count = 100000
        limit = 200000

        with open(json_file, 'r', encoding='utf-8') as file:
            for line in file:
                if count >= limit:
                    break

                try:
                    data = json.loads(line.strip())
                    if  data.get('author_id'):
                        author, created = Author.objects.get_or_create(
                            id=data['author_id'],
                            defaults={'name': data['author_name']}
                        )
                        book, created = Book.objects.get_or_create(
                            id=data['id'],
                            defaults={
                                'title': data['title'],
                                'author': author,
                                'isbn': data.get('isbn', ''),
                                'isbn13': data.get('isbn13', ''),
                                'language': data.get('language', ''),
                                'average_rating': data.get('average_rating', 0.0),
                                'ratings_count': data.get('ratings_count', 0),
                                'text_reviews_count': data.get('text_reviews_count', 0),
                                'publication_date': data.get('publication_date', ''),
                                'original_publication_date': data.get('original_publication_date', ''),
                                'format': f"{data.get('format', '')} {data.get('series_name')}",
                                'edition_information': data.get('edition_information', ''),
                                'image_url': data.get('image_url', ''),
                                'publisher': data.get('publisher', ''),
                                'num_pages': data.get('num_pages', None) if data.get('num_pages', None) else 0,
                                'description': data.get('description', '')
                            }
                        )

                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"Successfully processed book: {author.name} and book: {book.title}"))


                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f"Error decoding JSON: {e}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing data: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Import completed, processed {count} records'))