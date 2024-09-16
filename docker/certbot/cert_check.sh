#!/bin/sh

# Функция для вывода сообщений с меткой времени
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}
# Путь к SSL сертификатам
CERT_PATH="/etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/slow-news.sytes.net/privkey.pem"
# Бесконечный цикл для периодической проверки сертификатов
while true; do
    # Проверка существования сертификатов
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        log_message "Сертификаты не найдены. Генерация новых сертификатов..."
        certbot certonly --webroot --webroot-path=/yt/static --email fanomy90@gmail.com --agree-tos --no-eff-email --non-interactive -d slow-news.sytes.net
        if [ $? -eq 0 ]; then
            log_message "Новые сертификаты успешно сгенерированы. Перезапуск Nginx..."
            touch /tmp/renewed
            # Перезагрузка Nginx (раскомментировать при необходимости)
            # nginx -s reload
            log_message "Перезапуск Nginx произошел успешно"
        else
            log_message "Ошибка при генерации новых сертификатов."
        fi
    else
        log_message "Проверка актуальности сертификатов..."
        certbot renew --dry-run
        if [ $? -eq 0 ]; then
            log_message "Сертификаты актуальны (симуляция обновления)."
        else
            log_message "Обновление сертификатов..."
            certbot renew
            if [ $? -eq 0 ]; then
                log_message "Сертификаты успешно обновлены. Перезапуск Nginx..."
                touch /tmp/renewed
                # Перезагрузка Nginx (раскомментировать при необходимости)
                # nginx -s reload
                log_message "Перезапуск Nginx произошел успешно"
            else
                log_message "Ошибка при обновлении сертификатов."
            fi
        fi
    fi

    # Проверка флага обновления и перезагрузка Nginx, если необходимо
    if [ -f /tmp/renewed ]; then
        log_message "Обновленные сертификаты обнаружены. Перезагрузка Nginx..."
        docker exec nginx nginx -s reload
        if [ $? -eq 0 ]; then
            log_message "Перезапуск Nginx завершен."
        else
            log_message "Ошибка при перезапуске Nginx."
        fi
        rm /tmp/renewed
    fi
    # Пауза на 1 день (86400 секунд) перед следующей проверкой
    sleep 86400
    # sleep 604800  # 7 дней в секундах
done