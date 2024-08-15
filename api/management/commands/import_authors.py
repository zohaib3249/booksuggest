import json
from django.core.management.base import BaseCommand
from api.models import Author, Book, Work

class Command(BaseCommand):
    help = 'Import authors from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file to be imported')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        
        with open(json_file, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                try:
                    entry = json.loads(line)
                    author, created = Author.objects.update_or_create(
                        id=entry['id'],
                        defaults={
                            'name': entry['name'],
                            'gender': entry.get('gender', ''),
                            'image_url': entry.get('image_url', ''),
                            'about': entry.get('about', ''),
                            'fans_count': entry.get('fans_count', 0),
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"Successfully processed author: {author.name} and book: {author.name}"))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {line_number}: {e}")
                    continue  # Skip the malformed line
                