# тестовая обработка - сейчас выгружает данные из БД
import os
from django.core.management import call_command
from django.utils.timezone import now
from django.conf import settings

def parser_test():
    # Определяем путь для сохранения файла
    # output_dir = settings.BASE_DIR / 'news' / 'fixtures'
    # output_dir = settings.BASE_DIR / 'puppeteer' / 'news' / 'fixtures'
    output_dir = settings.BASE_DIR / 'SAVE'
    output_path = output_dir / 'news.json'
    
    # Проверяем, существует ли директория, если нет - создаем её
    if not os.path.exists(output_dir):
        print(str(now()) + ' не найдена директория для сохранения')

    try:
        # Запускаем команду dumpdata
        call_command('dumpdata', 'news', indent=2, output=output_path)
        print(str(now()) + ' parse test complete')
    except Exception as e:
        print(str(now()) + ' parse test failed with error: ' + str(e))

    return True
