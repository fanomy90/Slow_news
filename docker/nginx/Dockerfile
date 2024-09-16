FROM nginx:latest
# RUN rm /etc/nginx/conf.d/default.conf
# COPY nginx.conf /etc/nginx/conf.d
# COPY proxy_params /etc/nginx

# Dockerfile для Nginx
FROM nginx:latest

# Копируем конфигурацию Nginx в контейнер
COPY ./nginx.conf /etc/nginx/nginx.conf

# Копируем параметры прокси (если нужно)
COPY ./proxy_params /etc/nginx/proxy_params

# Убедитесь, что директивы для Certbot будут корректно работать
RUN mkdir -p /var/www/html

# Стандартная команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]