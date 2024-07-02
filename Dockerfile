FROM python:3.11.2
RUN apt-get update -y && apt-get upgrade -y
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./puppeteer ./puppeteer
CMD ["bash", "-c", "./puppeteer/manage.py makemigrations && ./puppeteer/manage.py migrate && ./puppeteer/manage.py runserver 0.0.0.0:9000"]