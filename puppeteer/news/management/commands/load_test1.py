import json
from django.core.management.base import BaseCommand
from news.models import News, Category

class Command(BaseCommand):
    help = 'Load data from JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

                for item in data:
                    model = item['model']
                    if model == 'news.news':
                        fields = item['fields']
                        News.objects.update_or_create(pk=item['pk'], defaults=fields)
                    elif model == 'news.category':
                        fields = item['fields']
                        Category.objects.update_or_create(pk=item['pk'], defaults=fields)

            self.stdout.write(self.style.SUCCESS('Data loaded successfully'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{json_file}" not found'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error decoding JSON from file "{json_file}"'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
