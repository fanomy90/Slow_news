import requests
import datetime
import time
import redis

API_KEY = "c3d9500417df01e0513292a8b7357c43"
API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Инициализация Redis-клиента
r = redis.StrictRedis(host='redis', port=6379, db=0)

CACHE_EXPIRATION = 3600  # 1 час в секундах

# Функция сохранения выбранного города анонимным пользователем
def save_user_city_selection(session_key, city_name):
    city_name = city_name.lower()
    r.sadd(f"user:{session_key}:cities", city_name)
    r.sadd("anonymous_user_cities", city_name)

# Функция получения прогноза погоды и сохранения в Redis
def get_weather(city_name, retries=6, backoff_factor=2):
    print(f"Запрос погоды для города: {city_name}")
    params = {
        'q': city_name,
        'units': 'metric',
        'appid': API_KEY
    }
    for attempt in range(retries):
        try:
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # weather_data = {
            #     'city': data['name'],
            #     'temperature': round(data['main']['temp']),
            #     'humidity': data['main']['humidity'],
            #     'wind_speed': round(data['wind']['speed']),
            #     'description': data['weather'][0]['description'],
            #     'timestamp': int(time.time())  # Текущее время как временная метка
            # }
            # Сохраняем все данные прогноза в Redis
            data['timestamp'] = int(time.time())  # Добавляем временную метку
            r.set(f"weather:{city_name}", json.dumps(data), ex=86400)  # Сохраняем данные с TTL 24 часа
            # Сохраняем данные погоды в Redis с TTL 24 часа
            # r.set(f"weather:{city_name}", json.dumps(weather_data), ex=86400)
            # return weather_data
            return data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе погоды для города {city_name}: {e}")
            time.sleep(backoff_factor ** attempt)
    print(f"Не удалось получить погоду для города {city_name} после {retries} попыток.")
    return None

# Функция получения прогноза из кэша Redis или через API с проверкой временной метки
def get_cached_weather(city_name):
    cached_weather = r.get(f"weather:{city_name}")
    if cached_weather:
        weather_data = json.loads(cached_weather)
        current_time = int(time.time())
        # Проверяем, если данные старше 1 часа, обновляем их
        if current_time - weather_data['timestamp'] > CACHE_EXPIRATION:
            print(f"Данные для {city_name} устарели, выполняем обновление...")
            weather_data = get_weather(city_name) or weather_data
        return weather_data
    else:
        return get_weather(city_name)

# Функция обновления погоды для всех выбранных анонимными пользователями городов
def update_anonymous_user_weather():
    cities = r.smembers("anonymous_user_cities")
    for city_name in cities:
        city_name = city_name.decode("utf-8")
        weather_data = get_cached_weather(city_name)
        if weather_data:
            print(f"Прогноз для {city_name}: {weather_data}")
        else:
            print(f"Не удалось обновить прогноз для города {city_name}")