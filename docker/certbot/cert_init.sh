#!/bin/sh

# Функция для вывода сообщений с меткой времени
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}
# Путь к SSL сертификатам
CERT_PATH="/etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/slow-news.sytes.net/privkey.pem"
domains="slow-news.sytes.net"
staging=0 # установить в 1 для тестирования работы сертификатов, 0 для выпуска рабочих сертификатов
email="fanomy90@gmail.com"
data_path="./data/certbot"

# создадим сертификат заглушку
gen_dummy_certs() {
    log_message "Генерация временных сертификатов для $domains..."
    # mkdir -p "$data_path/conf/live/$domains"
    mkdir -p /etc/letsencrypt/live/slow-news.sytes.net
    chmod -R 755 /etc/letsencrypt
    openssl req -x509 -nodes -newkey rsa:2048 -days 1\
        -keyout $KEY_PATH \
        -out $CERT_PATH \
        -subj '/CN=slow-news.sytes.net'
    if [ $? -ne 0 ]; then
        log_message "Ошибка при генерации временных сертификатов для $domains."
        continue
    else
        log_message "Временные сертификаты для $domains сгенерированы."
    fi
}
# удаление сертификата заглушки
del_dummy_certs() {
    log_message "Удаление временных сертификатов для $domains..."
    rm -Rf /etc/letsencrypt/live/$domains
    rm -Rf /etc/letsencrypt/archive/$domains
    rm -Rf /etc/letsencrypt/renewal/$domains.conf
}
# создадим рабочий сертификат
gen_work_certs() {
    docker start nginx
    sleep 10
    del_dummy_certs
    mkdir -p /etc/letsencrypt/live/slow-news.sytes.net
    chmod -R 755 /etc/letsencrypt
    log_message "Генерация рабочих сертификатов для $domains..."
    
    # docker-compose up --force-recreate -d nginx
    if [ $staging != "0" ]; then staging_arg="--staging"; fi
    certbot certonly --webroot \
        --webroot-path=/yt/static \
        $staging_arg \
        --email $email \
        --rsa-key-size 4096 \
        --agree-tos \
        --no-eff-email -d $domains \
        --force-renewal
    if [ $? -ne 0 ]; then
        log_message "Ошибка при генерации сертификатов для $domains."
        continue
    else
        log_message "Рабочие сертификаты для $domains сгенерированы."
    fi
}
# Бесконечный цикл для периодической проверки сертификатов
while true; do
    # Проверка существования сертификатов
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        # формирование временных сертификатов
        gen_dummy_certs
        if [ $? -eq 0 ]; then
            log_message "Инициализация запуска Nginx..."
            # установка флага перезапуска nginx
            # touch /tmp/renewed
        else
            log_message "Ошибка при генерации новых сертификатов для $domains."
        fi
        # формирование рабочих сертификатов
        gen_work_certs
        if [ $? -eq 0 ]; then
            log_message "Инициализация перезапуска Nginx..."
            # установка флага перезапуска nginx
            touch /tmp/renewed
        else
            log_message "Ошибка при генерации новых сертификатов."
        fi
    else
        log_message "Проверка актуальности сертификатов для $domains..."
        if openssl x509 -checkend 86400 -noout -in "$CERT_PATH"; then
            log_message "Сертификаты актуальны."
        else
            log_message "Сертификат истекает. Обновление..."
            certbot renew
            if [ $? -eq 0 ]; then
                log_message "Сертификаты успешно обновлены. Перезапуск Nginx..."
                touch /tmp/renewed
            else
                log_message "Ошибка при обновлении сертификатов."
            fi
        fi
    fi
    # Проверка флага обновления и перезагрузка Nginx
    if [ -f /tmp/renewed ]; then
        log_message "Перезапуск Nginx..."
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