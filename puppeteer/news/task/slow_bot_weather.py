def send_weather_forecast(subscribers):
    short_weather_subscribers = subscribers.filter(message_format="short")
    full_weather_subscribers = subscribers.filter(message_format="full")

    for subscriber in short_weather_subscribers:
        try:
            logging.info(f"Отправка краткого прогноза погоды пользователю {subscriber.chat_id}")
            message = 'Краткий прогноз погоды для города\nТемпература'
            send_message_with_retry(subscriber, message, None)
        except Exception as e:
            logging.error(f"Ошибка при отправке краткого прогноза погоды пользователю {subscriber.chat_id}: {e}")

    for subscriber in full_weather_subscribers:
        try:
            logging.info(f"Отправка полного прогноза погоды пользователю {subscriber.chat_id}")
            message = 'Полный прогноз погоды для города\nТемпература'
            send_message_with_retry(subscriber, message, None)
        except Exception as e:
            logging.error(f"Ошибка при отправке полного прогноза погоды пользователю {subscriber.chat_id}: {e}")


    # elif type_message == "weather":
        
    #     subscribers_to_short_weather = subscribers.filter(message_format="short")
    #     for subscriber in subscribers_to_short_weather:
    #         try:
    #             # Заглушка для погоды
    #             print(f"Отправка краткого прогноза погоды пользователю {subscriber.chat_id}")
    #             logging.info(f"Отправка краткого прогноза погоды пользователю {subscriber.chat_id}")
    #             image = None
    #             temp = "Температура"
    #             message = f'Краткий прогноз погоды для города\n' \
    #                     f'{temp}'
    #             success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
    #             if not success:
    #                 print(f"Ошибка при отправке краткого прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
    #                 logging.info(f"Ошибка при отправке краткого прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
    #         except Exception as e:
    #             print(f"Ошибка при отправке краткого прогноза пользователю {subscriber.chat_id}: {e}")
    #             logging.info(f"Ошибка при отправке краткого прогноза пользователю {subscriber.chat_id}: {e}")

    #     subscribers_to_full_weather = subscribers.filter(message_format="full")
    #     for subscriber in subscribers_to_full_weather:
    #         try:
    #             # Заглушка для погоды
    #             print(f"Отправка полного прогноза погоды пользователю {subscriber.chat_id}")
    #             logging.info(f"Отправка полного прогноза погоды пользователю {subscriber.chat_id}")
    #             image = None
    #             temp = "Температура"
    #             message = f'Полный прогноз погоды для города\n' \
    #                     f'{temp}'
    #             success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
    #             if not success:
    #                 print(f"Ошибка при отправке полного прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
    #                 logging.info(f"Ошибка при полного краткого прогноза погоды пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
    #         except Exception as e:
    #             print(f"Ошибка при отправке полного прогноза пользователю {subscriber.chat_id}: {e}")
    #             logging.info(f"Ошибка при отправке полного прогноза пользователю {subscriber.chat_id}: {e}")