from datetime import datetime
import time

def prepare_and_send_message(subscriber, formatted_date, subscriber_rates, message_format):
    from news.slow_bot import send_message_with_retry
    print(f"{datetime.now()} Подготовка сообщения курса валют для пользователя: {subscriber}")
    message_lines = [
        f'{list(rate.keys())[0]}: {list(rate.values())[0]} руб.'  # Получаем имя валюты и курс
        for rate in subscriber_rates
    ]
    if message_format == "short":
        message = f'Последние курсы валют на {formatted_date}\n\n' + '\n'.join(message_lines)
        image = None
    elif message_format == "full":
        message = f'Последние курсы валют на {formatted_date}\n\n' + '\n'.join(message_lines)
        # для полного сообщения будет картинка с графиком изменений курса за определенный период 
        image = None
    success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
    if success:
        print(f"{datetime.now()} Сообщение {message} курса валют успешно отправлено для пользователю {subscriber.username}")
    else:
        print(f"{datetime.now()} Ошибка при отправке сообщения {message} курса валют для пользователя {subscriber.username}")

def send_currency_frequency(frequency_sending="every_hour"):
    print(f'{datetime.now()} Запуск задачи рассылки курса валют из скрипта')
    from news.models import TelegramSubscriber, CurrencyRate, Currency
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")
    subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending, currency_sent=True)
    if not subscribers.exists():
        print(f"{datetime.now()} На рассылку курса валют с периодичностью {frequency_sending} нет подписчиков")
        return
    # Разделяем подписчиков по формату сообщений (короткие или полные)
    short_news_subscribers = subscribers.filter(message_format="short")
    full_news_subscribers = subscribers.filter(message_format="full")
    # Получаем валюты, на которые подписан хотя бы один пользователь
    subscribers_currencies = Currency.objects.filter(telegramsubscriber__subscribed_to_currency__isnull=False).distinct()
    # Получаем последние доступные курсы для этих валют
    latest_currency_rates = {
        currency.id: CurrencyRate.objects.filter(currency=currency).order_by('-date').first().rate
        for currency in subscribers_currencies
        if CurrencyRate.objects.filter(currency=currency).exists()
    }

    if short_news_subscribers.exists():
        for short_news_subscriber in short_news_subscribers:
            user_currencies = short_news_subscriber.subscribed_to_currency.all()
            
            subscriber_rates = [
                {currency.currency_name: latest_currency_rates[currency.id]}
                for currency in user_currencies
                if currency.id in latest_currency_rates
            ]
            prepare_and_send_message(short_news_subscriber, formatted_date, subscriber_rates, "short")
            print(f"{datetime.now()} Курсы валют для пользователя {short_news_subscriber.username}: {subscriber_rates}")


    if full_news_subscribers.exists():
        for full_news_subscriber in full_news_subscribers:
            user_currencies = full_news_subscriber.subscribed_to_currency.all()
            
            subscriber_rates = [
                {currency.currency_name: latest_currency_rates[currency.id]}
                for currency in user_currencies
                if currency.id in latest_currency_rates
            ]
            prepare_and_send_message(full_news_subscriber, formatted_date, subscriber_rates, "full")
            print(f"{datetime.now()} Курсы валют для пользователя {full_news_subscriber.username}: {subscriber_rates}")
