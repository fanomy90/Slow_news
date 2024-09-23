#!/bin/sh

# Функция для вывода сообщений с меткой времени
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}
# Путь к SSL сертификатам
CERT_PATH="/etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/slow-news.sytes.net/privkey.pem"

# Пути к конфигурационным файлам
HTTP_CONF_SRC="/opt/certbot/nginx-http.conf"
HTTPS_CONF_SRC="/opt/certbot/nginx-https.conf"
SSL_CONF_SRC="/opt/certbot/nginx-ssl.conf"
# Целевые директории для копирования конфигураций
NGINX_CONF_DIR="/etc/nginx/conf.d"

# Функция для замены конфигурационных файлов после создания сертификатов
replace_nginx_conf_files() {
    log_message "Замена конфигурационных файлов Nginx на HTTPS..."

    # Замена http конфигурации
    cp $HTTP_CONF_SRC $NGINX_CONF_DIR/nginx-http.conf

    # Замена https конфигурации (активируем SSL)
    cp $HTTPS_CONF_SRC $NGINX_CONF_DIR/nginx-https.conf

    # Замена ssl конфигурации
    cp $SSL_CONF_SRC $NGINX_CONF_DIR/nginx-ssl.conf

    log_message "Конфигурационные файлы заменены на SSL-конфигурацию."
}

# Бесконечный цикл для периодической проверки сертификатов
while true; do
    # Проверка существования сертификатов
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        # можно попробовать когда нет файлов принудительно добавлять файлы с временной конфигурацией
        log_message "Сертификаты не найдены. Генерация новых сертификатов..."
        # формирование сертификатов для рабочего домена
        # certbot certonly --webroot --webroot-path=/yt/static --email fanomy90@gmail.com --agree-tos --no-eff-email --non-interactive -d slow-news.sytes.net
        # формирование сертификатов для теста
        certbot certonly --staging --webroot --webroot-path=/yt/static --email fanomy90@gmail.com --agree-tos --no-eff-email -d slow-news.sytes.net
        if [ $? -eq 0 ]; then
            log_message "Новые сертификаты успешно сгенерированы. Перезапуск Nginx..."
            # Замена конфигурации на SSL
            replace_nginx_conf_files
            # установка флага перезапуска nginx
            touch /tmp/renewed
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
                # Замена конфигурации на SSL
                replace_nginx_conf_files
                установка флага перезапуска nginx
                touch /tmp/renewed
                log_message "Перезапуск Nginx произошел успешно"
            else
                log_message "Ошибка при обновлении сертификатов."
            fi
        fi
    fi

    # Проверка флага обновления и перезагрузка Nginx, если необходимо
    if [ -f /tmp/renewed ]; then
        log_message "Обновленные сертификаты обнаружены. Перезагрузка Nginx..."
        # docker exec nginx nginx -s reload
        docker restart nginx
        # docker restart nginx
        # curl -X POST http://host-docker-perform-restart
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