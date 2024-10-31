import requests
import datetime
import time

API_KEY = "c3d9500417df01e0513292a8b7357c43"
API_URL = "https://api.openweathermap.org/data/2.5/weather"

#функция получения прогноза погоды по городу
def get_weather(city, retries=6, backoff_factor=2):
    print(f"Запрос погоды для города: {city}")
    params = {
        'q': city.lower(),
        'units': 'metric',
        'appid': API_KEY
    }
    for attempt in range(retries):
        try:
            #response = requests.get(API_URL, params=params)
            response = requests.get(API_URL, params=params, timeout=30)  # например, 10 секунд
            print(f"Статус-код ответа: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"Полученные данные: {data}")
            weather_data = {
                'city': data['name'],
                'temperature': round(data['main']['temp']),
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'description': data['weather'][0]['description'] 
            }
            return weather_data
        except requests.exceptions.Timeout as e:
            print(f"Тайм-аут запроса для города {city}. Попытка {attempt + 1} из {retries}. Ошибка {e}")
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка HTTP {response.status_code} для города {city}: {e}")
            break  # Прекращаем попытки для других ошибок HTTP
        except requests.exceptions.RequestException as e:
            print(f'ошибка API запроса данных прогноза погоды {e}')
        # Ожидание перед повторной попыткой
        time.sleep(backoff_factor ** attempt)
    print(f"Не удалось получить погоду для города {city} после {retries} попыток.")
    return None
#функция подготовки сообщения с прогнозом погоды
def prepare_and_send_message(subscribers, city, weather, message_format):
    from news.slow_bot import send_message_with_retry
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for subscriber in subscribers:
        if message_format == "short":
            message = (
                f'Прогноз погоды в городе {city} на {now}\n\n'
                f'Температура {weather["temperature"]}\n'
                f'Влажность {weather["humidity"]}\n'
                f'Ветер {weather["wind_speed"]}\n'
                f'Дополнительно {weather["description"]}'
            )
        elif message_format == "full":
            message = (
                f'Прогноз погоды в городе {city} на {now}\n\n'
                f'Температура {weather["temperature"]}\n'
                f'Влажность {weather["humidity"]}\n'
                f'Ветер {weather["wind_speed"]}\n'
                f'Дополнительно {weather["description"]}'
            )
        image = None
        success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
        if success:
            print(f"{now} Сообщение {message} прогноза погоды успешно отправлено пользователю {subscriber.username}")
        else:
            print(f"{now} Ошибка при отправке сообщения {message} прогноза погоды пользователю {subscriber.username}")
#функция получения данных для подготовки сообщения
def send_weather_frequency(frequency_sending="every_hour"):
    now = datetime.datetime.now()
    print(f"{now} Запуск подбора подписчиков для прогноза погоды")
    from news.models import TelegramSubscriber, City
    subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending, weather_sent=True)
    if not subscribers.exists():
        print(f"{now} На рассылку прогноза погоды с периодичностью {frequency_sending} нет подписчиков")
        return
    #новый вариант обработки подписчиков прогноза погоды
    cities = City.objects.filter(telegramsubscriber__subscribed_weather_city__isnull=False).distinct()
    if not cities.exists():
        print(f"{now} Нет подписчиков которые выбрали город для прогноза погоды")
        return
    for city in cities:
        weather = get_weather(city.city_name)
        if weather:
            short_message_subscribers = subscribers.filter(message_format="short")
            full_message_subscribers = subscribers.filter(message_format="full")
            
            if short_message_subscribers.exists():
                prepare_and_send_message(short_message_subscribers.filter(subscribed_weather_city=city), city, weather, "short")
            if full_message_subscribers.exists():
                prepare_and_send_message(full_message_subscribers.filter(subscribed_weather_city=city), city, weather, "full")
        else:
            print(f"Не удалось получить погоду для города {city.city_name}")