# FOODGRAM - Продуктовый помощник
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других авторов, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов.

## Технологии:
- Python
- Django Rest Framework
- Postgres
- Docker
- nginx
- gunicorn

## Квикстарт:
1) Склонируйте репозитрий на свой компьютер.
2) Создайте .env файл в директории infra/, в котором должны содержаться следующие переменные:
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME= # название БД\ POSTGRES_USER= # ваше имя пользователя
- POSTGRES_PASSWORD= # пароль для доступа к БД
- DB_HOST=db
- DB_PORT=5432\
3) Из папки infra/ соберите образ при помощи docker-compose $ docker-compose up -d --build
4) Примените миграции $ docker-compose exec web python manage.py migrate
5) Соберите статику $ docker-compose exec web python manage.py collectstatic --no-input
6) Для доступа к админке не забудьте создать суперюзера $ docker-compose exec web python manage.py createsuperuser.

## Авторы: 
- [Вихляев Василий](https://github.com/BasilVik) - разработка бэкэнда и настройка деплоя. 
- [Яндекс.Практикум](https://github.com/yandex-praktikum) - разработка фронтенда.
