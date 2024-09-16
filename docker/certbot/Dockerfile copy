FROM certbot/certbot

# Копируем наши скрипты в контейнер
COPY cert_check.sh /usr/local/bin/cert_check.sh
COPY cert_update.sh /usr/local/bin/cert_update.sh

# Делаем скрипты исполняемыми
RUN chmod +x /usr/local/bin/cert_check.sh
RUN chmod +x /usr/local/bin/cert_update.sh

# Команда для запуска скрипта обновления при старте контейнера
CMD ["/usr/local/bin/cert_update.sh"]