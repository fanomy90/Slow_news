def get_subscribers_to_news(subscribers, category, message_format):
    return subscribers.filter(subscribed_to_categories=category, message_format=message_format)


def prepare_and_send_news(subscribers, article, category_style, content, image, message_format):
    for subscriber in subscribers:
        message = (
            f'{category_style} <b>{article.category.name} {article.date}</b>\n\n'
            f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n'
            f'{content}\n'
            f'{trim_author(article.author)}'
        )
        logging.info(f"Отправка {message_format} новостного сообщения пользователю {subscriber.chat_id}")
        success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
        if not success:
            logging.error(f"Ошибка при отправке {message_format} сообщения пользователю {subscriber.chat_id}")

def send_news(type_message="news", frequency_sending="every_hour"):
    from news.models import TelegramSubscriber, News, Category
    subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending)

    if type_message == "news":
        categories = Category.objects.all()
        category_styles = {
            'Безопасность': '🔒',
            'Статьи': '📄',
            'Обзоры': '🔍',
            'Интервью': '🗣️',
        }

        for category in categories:
            news = News.objects.filter(cat=category, is_published=True, is_sent=False)
            if news.exists():
                for article in news:
                    category_style = category_styles.get(category.name, 'i')
                    image = article.image if article.image else None

                    # Для коротких новостей
                    short_news_subscribers = get_subscribers_to_news(subscribers, category, "short")
                    short_content = trim_content(article.content, word_limit=35)
                    prepare_and_send_news(short_news_subscribers, article, category_style, short_content, image, "короткое")

                    # Для полных новостей
                    full_news_subscribers = get_subscribers_to_news(subscribers, category, "full")
                    full_content = article.content
                    prepare_and_send_news(full_news_subscribers, article, category_style, full_content, image, "полное")

                    # Отмечаем новость как отправленную
                    article.is_sent = True
                    article.save()
                    logging.info(f"Новость {article.title} помечена как отправленная.")
            else:
                logging.info(f"В категории {category.name} нет новостей для отправки.")



# def send_news(type_message="news", frequency_sending="every_hour"):
#     from news.models import TelegramSubscriber, News, Category  # Отложенный импорт здесь, добавить модель городов для прогноза и модель валют
#     today = datetime.date.today()
#     subscribers = TelegramSubscriber.objects.filter(frequency_sending=frequency_sending)

#     if type_message == "news":
#         print(f"Выполняется подготовка сообщения новостной рассылки")
#         logging.info(f"Выполняется подготовка сообщения новостной рассылки")
#         categories = Category.objects.all()
        
#         for category in categories:
#             print(f"Получаем новости по категориям")
#             logging.info(f"Получаем новости по категориям")
#             news = News.objects.filter(cat=category, is_published=True, is_sent=False)

#             if news.exists():
#                 for article in news:
#                     if not article.is_sent:
#                         print(f"Формируем сообщение")
#                         logging.info(f"Формируем сообщение")
#                         category_styles = {
#                             'Безопасность': '🔒',
#                             'Статьи': '📄',
#                             'Обзоры': '🔍',
#                             'Интервью': '🗣️',
#                         }
#                         category_style = category_styles.get(category.name, 'i')
#                         author = trim_author(article.author)

#                         #переделать чтобы формировалось два типа сообщений и отправлялись пользователям
#                         # if message_format == 'full':
#                         #     content = article.content
#                         # else:
#                         #     content = trim_content(article.content, world_limit=35)

#                         image = article.image if article.image else None

#                         # Отправляем сообщение только тем пользователям, кто подписан на короткие типы новостей по категориям
#                         subscribers_to_short_news = subscribers.filter(subscribed_to_categories=category, message_format="short")
#                         for subscriber in subscribers_to_short_news:
#                             content = trim_content(article.content, world_limit=35)
#                             message = f'{category_style} <b>{category.name} {article.date}</b>\n\n' \
#                                     f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n' \
#                                     f'{content}\n' \
#                                     f'{author}'
                            
#                             print(f"Отправка короткого новостного сообщения пользователю {subscriber.chat_id}")
#                             logging.info(f"Отправка короткого новостного сообщения пользователю {subscriber.chat_id}")
#                             success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
#                             if not success:
#                                 print(f"Ошибка при отправке короткого сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
#                                 logging.info(f"Ошибка при отправке короткого сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
#                         # Отправляем сообщение только тем пользователям, кто подписан на полные типы новостей по категориям
#                         subscribers_to_full_news = subscribers.filter(subscribed_to_categories=category, message_format="full")
#                         for subscriber in subscribers_to_full_news:
#                             content = article.content
#                             message = f'{category_style} <b>{category.name} {article.date}</b>\n\n' \
#                                     f'<a href="https://slow-news.sytes.net{article.get_absolute_url()}">{article.title}</a>\n' \
#                                     f'{content}\n' \
#                                     f'{author}'
                            
#                             print(f"Отправка длинного новостного сообщения пользователю {subscriber.chat_id}")
#                             logging.info(f"Отправка длинного новостного сообщения пользователю {subscriber.chat_id}")
#                             success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
#                             if not success:
#                                 print(f"Ошибка при отправке длинного сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
#                                 logging.info(f"Ошибка при отправке длинного сообщения пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")

#                         # Помечаем новость как отправленную
#                         print(f"Новость {article.title} помечена как отправленная.")
#                         logging.info(f"Новость {article.title} помечена как отправленная.")
#                         article.is_sent = True
#                         article.save()

#             else:
#                 print(f"В категории {category.name} нет новостей для отправки.")
#                 logging.info(f"В категории {category.name} нет новостей для отправки.")
