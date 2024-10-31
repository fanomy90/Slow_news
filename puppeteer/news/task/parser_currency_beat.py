import requests
from datetime import datetime
import time
from celery import shared_task, Celery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery.exceptions import SoftTimeLimitExceeded
from django.db import transaction, IntegrityError
from decimal import Decimal

# async def send_task_status(task_id, status, message):
def send_task_status(task_id, status, message):
    channel_layer = get_channel_layer()
    #await channel_layer.group_send(f"task_{task_id}", {"type": "task_status", "status": status, "message": message,})
    async_to_sync(channel_layer.group_send)(
        f"task_{task_id}",
        {"type": "task_status", "status": status, "message": message}
    )

API_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/";

def get_currency(task_id=1, mode="rub", retries=3, backoff_factor=2, timeout=30):
    # task_id = self.request.id
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'Запрос курса валют на {date}')
    send_task_status(task_id, "PROGRESS", f"Запрос курса валют на {date}")
    for attempt in range(retries):
        now = datetime.now()
        response = None
        try:
            # response = requests.get(API_URL, params=params, timeout=30)
            #response = await fetch(API_URL + mode + '.json', timeout=timeout);
            #response = requests.get(f"{API_URL}{mode}.json", timeout=timeout)
            response = requests.get(f"{API_URL}{mode}.json", timeout=timeout)
            print(f"{now} Ответ от сервиса курса валют: {response.status_code}")
            send_task_status(task_id, "PROGRESS", f"{now} Ответ от сервиса курса валют: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            # print(f"{now} Получены данные: {data}")
            # async_to_sync(send_task_status)(task_id, "SUCCESS", f"{now} Данные успешно получены.")
            return data
        except requests.exceptions.Timeout as e:
            print(f"{now} Тайм-аут запроса курса валют для {mode}. Попытка {attempt + 1} из {retries}. Ошибка {e}")
            send_task_status(task_id, "PROGRESS", f"{now} Тайм-аут запроса курса валют для {mode}. Попытка {attempt + 1} из {retries}. Ошибка {e}")
        except requests.exceptions.HTTPError as e:
            if response is not None:
                print(f"{now} Ошибка HTTP {response.status_code} для {mode}: {e}")
                send_task_status(task_id, "FAILURE", f"{now} Ошибка HTTP {response.status_code} для {mode}: {e}")
            else:
                print(f"{now} Ошибка HTTP для {mode}: {e}")
                send_task_status(task_id, "FAILURE", f"{now} Ошибка HTTP для {mode}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"{now} Ошибка API запроса получения курса валют: {e}")
            send_task_status(task_id, "FAILURE", f"{now} Ошибка API запроса получения курса валют: {e}")
        except SoftTimeLimitExceeded:
            print(f"{now} Задача была прервана из-за превышения мягкого лимита времени.")
            send_task_status(task_id, "FAILURE", f"{now} Задача прервана из-за превышения лимита времени.")
            # return None
            raise  # Повторно вызываем исключение, чтобы остановить выполнение задачи
        time.sleep(backoff_factor ** attempt)
        print(f"{now} Ошибка при получении данных. Ожидание перед повторной попыткой...")
        send_task_status(task_id, "FAILURE", f"{now} Ошибка при получении данных. Ожидание перед повторной попыткой...")
    print(f"Не удалось получить данные после {retries} попыток.")
    send_task_status(task_id, "FAILURE", f"Не удалось получить данные после {retries} попыток.")
    return None

def import_currency(task_id, currency, mode="rub"):
    from news.models import CurrencyRate, Currency
    from django.db import transaction, IntegrityError
    from datetime import datetime

    now = datetime.now()
    print(f'{now} Запущен импорт курса валют в базу данных')
    send_task_status(task_id, "PROGRESS", f"{now} Запущен импорт курса валют в базу данных")
    currency_date = currency['date']
    currency_rub = currency.get(mode)
    currencies = {currency.symbol: currency for currency in Currency.objects.all()}
    # Получаем существующие курсы на дату и создаем словарь для быстрого поиска
    existing_rates = CurrencyRate.objects.filter(date=currency_date).values_list('currency__symbol', flat=True)
    existing_rates_set = set(existing_rates)  # Используем множество для быстрой проверки
    successful_imports = 0
    skipped_imports = 0
    for currency_symbol, rate in currency_rub.items():
        normalize = round(1 / rate, 4)
        # Приводим символы к одному регистру для корректного сравнения
        if currency_symbol.lower() in existing_rates_set:
            skipped_imports += 1
            print(f"{datetime.now()} Курс валюты на {currency_symbol}:{normalize} на {currency_date} уже есть в базе и будет пропущен")
            send_task_status(task_id, "PROGRESS", f"{datetime.now()} Курс валюты на {currency_symbol}:{normalize} на {currency_date} уже есть в базе и будет пропущен")
        else:
            try:
                with transaction.atomic():
                    currency_instance = currencies.get(currency_symbol)
                    if currency_instance is None:
                        print(f"Валюта с символом {currency_symbol} не найдена. Создаем новую валюту.")
                        currency_instance = Currency.objects.create(symbol=currency_symbol, currency_name=currency_symbol.upper())
                    # Проверяем, существует ли курс перед его добавлением
                    existing_rate = CurrencyRate.objects.filter(currency=currency_instance, date=currency_date).first()
                    if existing_rate:
                        print(f"{datetime.now()} Курс валюты на {currency_symbol} уже существует на {currency_date} и будет пропущен.")
                        send_task_status(task_id, "PROGRESS", f"{datetime.now()} Курс валюты на {currency_symbol} уже существует на {currency_date} и будет пропущен.")
                        continue  # Пропускаем добавление курса, если он уже есть
                    CurrencyRate.objects.create(currency=currency_instance, date=currency_date, rate=normalize)
                    successful_imports += 1
                    print(f"{datetime.now()} Курс валюты на {currency_symbol}:{normalize} на {currency_date} добавлен в базу")
                    send_task_status(task_id, "PROGRESS", f"{datetime.now()} Курс валюты на {currency_symbol}:{normalize} на {currency_date} добавлен в базу")
            except IntegrityError as e:
                print(f"Ошибка при добавлении курса валюты: {e}")
                send_task_status(task_id, "FAILURE", f"Ошибка при добавлении курса валюты: {e}")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                send_task_status(task_id, "FAILURE", f"Произошла ошибка: {e}")
    return successful_imports, skipped_imports

@shared_task(bind=True, time_limit=60, soft_time_limit=30)
def currency_beat(self, mode="rub", retries=3, backoff_factor=2, timeout=30):
    task_id = self.request.id
    now = datetime.now()
    print(f'{now} Запуск задачи получения и импорта курса валют в базу данных')
    # async_to_sync(send_task_status)(task_id, "PROGRESS", f"{now} Запуск задачи получения и импорта курса валют в базу данных")
    send_task_status(task_id, "PROGRESS", f"{now} Запуск задачи получения и импорта курса валют в базу данных")
    #получим текущие данные курса валют
    currency = get_currency(task_id=task_id, mode=mode)
    if currency:
        # print(f"{now} Данные курса валют успешно получены: {currency}")
        # async_to_sync(send_task_status)(task_id, "SUCCESS", f"{now} Данные курса валют успешно получены: {currency}")
        send_task_status(task_id, "PROGRESS", f"{now} Данные курса валют успешно получены: {currency}")
        
        #currency_data = import_currency(task_id=task_id, currency=currency, mode=mode)
        successful_imports, skipped_imports = import_currency(task_id=task_id, currency=currency, mode=mode)
        if successful_imports > 0 or skipped_imports > 0:
            print(f"{datetime.now()} Курсы валюты  были успешно импортированы в базу: добавлено {successful_imports}, пропущено {skipped_imports}")
            send_task_status(task_id, "SUCCESS", f"{datetime.now()} Курсы валюты были успешно импортированы в базу: добавлено {successful_imports}, пропущено {skipped_imports}")
        else:
            print(f"{datetime.now()} Курсы валюты не были импортированы из за ошибки:добавлено {successful_imports}, пропущено {skipped_imports}")
            send_task_status(task_id, "FAILURE", f"{datetime.now()} Курсы валюты не были импортированы из за ошибки:добавлено {successful_imports}, пропущено {skipped_imports}")
    else:
        print(f"{now} Данные курса валют не были получены")
        # async_to_sync(send_task_status)(task_id, "FAILURE", f"{now} Данные курса валют не были получены")
        send_task_status(task_id, "FAILURE", f"{now} Данные курса валют не были получены")