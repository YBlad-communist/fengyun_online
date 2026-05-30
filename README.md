# Фэнъюнь — Django-магазин азиатских товаров

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env (скопировать из .env.example и заполнить)
cp .env.example .env

# 3. Миграции и тестовые данные
python manage.py migrate
python manage.py loaddata shop/fixtures/initial_data.json

# 4. Создать суперпользователя
python manage.py createsuperuser

# 5. Запустить
python manage.py runserver
```

Сайт: http://127.0.0.1:8000  
Админка: http://127.0.0.1:8000/admin

## Telegram-уведомления

В `.env` заполните:
- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather
- `TELEGRAM_ADMIN_CHAT_ID` — ваш chat_id (узнать через @userinfobot)

## Структура

```
fengyun/
├── fengyun/          # Настройки проекта
├── shop/             # Основное приложение
│   ├── models.py     # Country, Product, Order, PickupPoint, UserProfile
│   ├── views.py      # Каталог, корзина, заказы, аккаунт
│   ├── forms.py      # OrderForm, RegisterForm, ProfileForm
│   ├── admin.py      # Настроенная админка
│   ├── fixtures/     # Стартовые данные (страны, точки, товары)
│   └── templates/    # Шаблоны
├── templates/        # base.html
└── static/css/       # style.css (белый/жёлтый/чёрный)
```

## Точки выдачи (Находка)
- Находка-Мега
- Клён
- Меридиан
- Экодом

## Функции
- ✅ Каталог с фильтром по странам
- ✅ Корзина (Django sessions)
- ✅ Оформление заказа с выбором точки самовывоза
- ✅ Страница товаров под заказ (in_stock=False)
- ✅ Личный кабинет + бонусная система (1 балл / 100₽)
- ✅ Карта магазинов (Leaflet + OpenStreetMap)
- ✅ Telegram-уведомления при новом заказе
- ✅ Bootstrap 5 + цвета белый/жёлтый/чёрный
- ✅ Расширенная Django-админка
