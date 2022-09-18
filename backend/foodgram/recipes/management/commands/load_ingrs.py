import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        data_path = os.path.join(settings.BASE_DIR, "data/")
        with open(
            f'{data_path}ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            fieldnames = ('name', 'measurement_unit',)
            reader = csv.DictReader(file, fieldnames=fieldnames)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader)
        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
