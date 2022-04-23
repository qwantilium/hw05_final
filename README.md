#Yatube 
## Описание проекта:
#####Социальная сеть для публикации личных дневников.
Стек: Python 3, Django, PostgreSQL, gunicorn, nginx, Яндекс.O6naKo(Ubuntu 20.04), pytest, Git.
[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

Разработан по классической MVT архитектуре. 
Используется пагинация постов и кэширование.
Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту.

Написаны тесты, проверяющие работу сервиса по моделям, URLs, Views, контекста, Forms.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/qwantilium/hw05_final.git
```

Cоздать и активировать виртуальное окружение(Linux):

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейти в рабочую директорию
```
cd yatube
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```