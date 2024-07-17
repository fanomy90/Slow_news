#тестовый скрипт загрузки дампа данных в бд
import os
from django.core.management import call_command
from django.utils.timezone import now
from django.conf import settings

def loader_test1():
    input_dir = settings.BASE_DIR / 'SAVE'
    input_path = input_dir / 'news.json'
    
    print(str(now()) + ' Начало выполнения loader_test')
    print('Путь к файлу: ' + str(input_path))

    if not os.path.exists(input_path):
        print(str(now()) + ' Файл для загрузки не найден по пути: ' + str(input_path))
        return False

    try:
        call_command('loaddata', str(input_path))
        print(str(now()) + ' тестовый импорт выполнен')
    except Exception as e:
        print(str(now()) + ' тестовый импорт завершился с ошибкой: ' + str(e))
        return False
    
    return True