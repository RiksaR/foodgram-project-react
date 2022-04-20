# Foodgram

## Краткое описание проекта
Foodgram - продуктовый помощник, где можно поделиться своими рецептами и
секретами приготовления различных блюд. Для того, чтобы запустить проект, нужно
установить и настроить Docker. Как это сделать, можно найти по ссылке:
https://timeweb.com/ru/community/articles/ustanovka-i-nastroyka-docker-1. Далее
необходимо клонировать репозиторий с помощью команды 
```python
    git clone <адрес репозитория>
```
После этого необходимо зайти в директорию проекта и создать файл .env,
заполнив его данными.

### Шаблон наполнения env-файла
```
DB_NAME='postgres' # имя базы данных
POSTGRES_USER='postgres' # логин для подключения к базе данных
POSTGRES_PASSWORD='postgres' # пароль для подключения к БД
DB_HOST='db' # название сервиса (контейнера)
DB_PORT='5432' # порт для подключения к БД
SECRET_KEY='...' # секретный ключ Django-проекта
```

После клонирования репозитория с сайта https://github.com и создания файла .env
необходимо зайти в папку infra и выполнить следующие действия:

cобрать образ
```python
    docker-compose up -d --build
```
применить миграции
```python
    docker-compose exec backend python manage.py migrate
```
создать суперюзера
```python
    docker-compose exec backend python manage.py createsuperuser
```
применить команду для сбора статики в папку static/
```python
    docker-compose exec backend python manage.py collectstatic --no -input
```
применить команду для загрузки ингредиентов в базу данных
```python
    docker-compose exec backend python manage.py load_data
```
Для остановки приложения используйте команду
```python
    docker-compose down -v
```

### Используемые технологии
Python 3.9  
Django 4.0.3  
Gunicorn 20.0.4  
Nginx 1.19.3  
Docker 20.10.7  

### Автор проекта:
Смоленский Алексей
