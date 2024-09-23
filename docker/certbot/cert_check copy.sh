#!/bin/sh

# Функция для вывода сообщений с меткой времени
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}
# Путь к SSL сертификатам
CERT_PATH="/etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/slow-news.sytes.net/privkey.pem"
NGINX_CONF_PATH="/etc/nginx/conf.d/nginx-ssl.conf"

# Функция для создания файла конфигурации для HTTPS
create_nginx_ssl_conf() {
    # Путь к конфигурационному файлу для HTTPS
    NGINX_CONF_PATH="/etc/nginx/conf.d/nginx-ssl.conf"

    # Создаем файл конфигурации для HTTPS
    cat > $NGINX_CONF_PATH <<EOL
server {
    listen 443 ssl;
    server_name slow-news.sytes.net;

    # Пути к SSL сертификатам
    ssl_certificate /etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/slow-news.sytes.net/privkey.pem;

    # Настройки SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'HIGH:!aNULL:!MD5';

    # Проксирование запросов на бэкенд
    location / {
        proxy_pass http://puppeteer:9000;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    # Обработка статических файлов
    location /static/ {
        alias /yt/static/;
        autoindex on;
        types { 
            text/css css; 
        }
        access_log /var/log/nginx/static_access.log;
        log_not_found on;
    }

    # Обработка веб-сокетов
    location /ws/ {
        proxy_pass http://puppeteer:9000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
    }

    # Логирование ошибок и запросов
    error_log /var/log/nginx/error.log debug;
    access_log /var/log/nginx/access.log;
}
EOL
}

# Бесконечный цикл для периодической проверки сертификатов
while true; do
    # Проверка существования сертификатов
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        log_message "Сертификаты не найдены. Генерация новых сертификатов..."
        certbot certonly --webroot --webroot-path=/yt/static --email fanomy90@gmail.com --agree-tos --no-eff-email --non-interactive -d slow-news.sytes.net
        if [ $? -eq 0 ]; then
            log_message "Новые сертификаты успешно сгенерированы. Перезапуск Nginx..."
            # создание файла конфигурации https
            create_nginx_ssl_conf
            # перезапуск nginx
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
                # создание файла конфигурации https
                create_nginx_ssl_conf
                # перезапуск nginx
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