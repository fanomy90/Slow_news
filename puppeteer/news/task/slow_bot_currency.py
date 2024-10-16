def send_currency_updates(subscribers):
    for subscriber in subscribers:
        try:
            logging.info(f"Отправка курса валют пользователю {subscriber.chat_id}")
            message = 'Курс валют на сегодня\nСписок валют'
            send_message_with_retry(subscriber, message, None)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения курса валют пользователю {subscriber.chat_id}: {e}")

    # elif type_message == "currency":
    #     for subscriber in subscribers:
    #         try:
    #             # Заглушка для курса валют
    #             image = None
    #             currency = "Список валют"
    #             message = f'Курс валют на \n' \
    #                     f'{currency}'
    #             success = send_message_with_retry(subscriber, message, image, retries=3, delay=3)
    #             if not success:
    #                 print(f"Ошибка при отправке курса валют пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
    #                 logging.info(f"Ошибка при отправке курса валют пользователю {subscriber.chat_id}: повторные попытки не увенчались успехом")
                        
    #             print(f"Отправка курсов валют пользователю {subscriber.chat_id}")
    #             logging.info(f"Отправка курсов валют пользователю {subscriber.chat_id}")
    #         except Exception as e:
    #             print(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}")
    #             logging.info(f"Ошибка при отправке сообщения пользователю {subscriber.chat_id}: {e}")
