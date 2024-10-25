FROM certbot/certbot:latest
# Используем Alpine пакетный менеджер для установки docker-cli
RUN apk add --no-cache docker-cli
# Создайте директорию для логов
RUN mkdir -p /var/log/certbot
# RUN mkdir -p /etc/nginx/conf.d
# Копируем наши скрипты в контейнер
# COPY ./cert_check.sh /usr/local/bin/cert_check.sh
COPY ./cert_init.sh /usr/local/bin/cert_init.sh
# COPY ./nginx-ssl.conf /etc/nginx/conf.d/nginx-ssl.conf
# копируем каталог с кусками конфига nginx для сборки ssl конфигурации
# COPY ./tmp ./
# Делаем скрипты исполняемыми
# RUN chmod +x /usr/local/bin/cert_check.sh \
#     && ls -l /usr/local/bin
RUN chmod +x /usr/local/bin/cert_init.sh\
    && ls -l /usr/local/bin
# Запуск скрипта обновления при старте контейнера
# CMD ["/usr/local/bin/cert_check.sh"]
CMD ["/usr/local/bin/cert_init.sh"]