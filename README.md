# Foodgram
[![foodgram_project](https://github.com/Kenzzu/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Kenzzu/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
![Foodgram](https://github.com/Kenzzu/foodgram-project-react/blob/main/static/images/logo.png)

Foodgram - это веб-приложение, которое позволяет пользователям находить, публиковать и собирать рецепты. Оно предоставляет платформу для любителей кулинарии, где они могут поделиться своими любимыми рецептами и создавать персонализированный список покупок на основе добавленных рецептов. Проект является открытым и доступен на [GitHub](https://github.com/Kenzzu/foodgram-project-react.git).

## Функциональность

- Регистрация пользователя: Пользователи могут зарегистрировать аккаунт в Foodgram, чтобы получить доступ ко всем функциям приложения.
- Создание рецептов: Зарегистрированные пользователи могут создавать и публиковать свои собственные рецепты, делая их доступными для сообщества Foodgram.
- Поиск рецептов: Пользователи могут исследовать широкий спектр рецептов, представленных другими участниками сообщества.
- Список покупок: Пользователи могут создавать список покупок на основе добавленных рецептов, чтобы легко организовать свои покупки перед готовкой. 

## Установка и запуск проекта

```bash
# Создайте и активируйте виртуальное окружение
python -m venv env
source env/bin/activate

# Создайте файл .env и добавьте параметры
cd infra/
echo "SECRET_KEY=секретный_ключ_django" >> .env
echo "DB_ENGINE=django.db.backends.postgresql" >> .env
echo "DB_NAME=postgres" >> .env
echo "POSTGRES_USER=postgres" >> .env
echo "POSTGRES_PASSWORD=postgres" >> .env
echo "DB_HOST=db" >> .env
echo "DB_PORT=5432" >> .env

# Установите зависимости
cd ../backend/
pip install -r requirements.txt

# Выполните миграции
python manage.py migrate

# Запустите сервер
python manage.py runserver

## Используемые технологии
В проекте используются следующие технологии:

- **Python**: Язык программирования, на котором написан проект.
- **Django**: Фреймворк для разработки веб-приложений на языке Python.
- **DRF (Django Rest Framework)**: Мощный фреймворк для создания RESTful API на базе Django.
- **PostgreSQL**: Реляционная база данных, используемая для хранения данных в проекте.
- **Yandex.Cloud**: Облачная платформа, используемая для развертывания и хостинга проекта.
- **GitHub Actions**: Сервис автоматизации разработки и CI/CD интеграции, используемый для непрерывной сборки, тестирования и развертывания проекта.

## Автор
Проект разработан [Олегом Киселевым](https://github.com/Kenzzu/).
## Фронтенд
Фронтенд проекта предоставлен [Яндекс.Практикумом](https://praktikum.yandex.ru/)


Сайт доступен по адресу: http://foodgram-kenzzu.sytes.net/
Админ: Kenzzu
Пароль: e85735237