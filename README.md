## Проект Price monitoring

микросервисное веб приложение для мониторинга цен на М.видео. 
Необходимо предусмотрен следующий функционал:

1. Модуль HTTP API содержащий следующие маршруты:
- Добавление нового товара на мониторинг (ссылка на товар)
- Удаление товара 
- Получение списка товаров на мониторинге 
- Получение истории цен на товар.

2. Телеграм бот с аналогичным функционалом

3. Модуль мониторинга, который будет периодически получать новую цену товара.


### Технологии:

Python, FastAPI, Docker, Gunicorn, PostgreSQL, Aiogram

### Запуск проекта:

- Клонировать репозиторий:
```
git@github.com:krankir/price_monitoring_product.git
```
- Создать и запустить контейнеры Docker
```
sudo docker compose up -d
```
- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```


### Запуск проекта на локальной машине:

- Клонировать репозиторий:
```
git@github.com:krankir/price_monitoring_product.git
```

- В директории price_monitoring_product файл example.env переименовать в .env-non-dev и заполнить своими данными:
```
DB_HOST=db_host
DB_PORT=db_port
DB_NAME=db_name
DB_USER=db_user
DB_PASS=db_pass

POSTGRES_DB=db_name
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_pass


TOKEN=telegram_bot_tocken
```

- Создать и запустить контейнеры Docker, как указано выше.

- Документация будет доступна по адресу: [документация](http://localhost/docs#/)

- Телеграм бот будет доступен по адресу: [Телеграм бот](https://t.me/Mvideo_Scrap_PriceBot)

### Автор backend'а:

Редько Анатолий 2023 г.