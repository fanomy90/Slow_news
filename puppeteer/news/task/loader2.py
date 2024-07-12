import os
from django.core.management import call_command
from django.utils.timezone import now
from django.conf import settings
    
    
def loader_test2():
    input_dir = settings.BASE_DIR / 'SAVE'
    # input_dir = settings.BASE_DIR / 'news' / 'fixtures'
    input_path = input_dir / 'news.json'
    if not os.path.exists(input_path):
        print(str(now()) + ' Файл для загрузки не найден по пути: ' + str(input_path))
        return False
    try:
        # Запускаем команду dumpdata
        # call_command('loaddata', 'news.json')

        # Выводим список файлов в каталоге input_dir
        files = os.listdir(input_dir)
        print(str(now()) + ' Список файлов в каталоге ' + str(input_dir) + ':')
        for file in files:
            print(file)
            
        print(str(now()) + ' тестовый импорт выполнен')
    except Exception as e:
        print(str(now()) + ' тестовый импорт завершился с ошибкой: ' + str(e))
        return False
    return True