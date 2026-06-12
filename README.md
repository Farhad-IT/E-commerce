# E-commerce project (Backend)

Современный e-commerce проект для просмотра товаров, добавления их в корзину и оформления заказа.

Этот проект представляет собой серверную часть интернет-магазина, в котором пользователь может:
- просматривать каталог товаров;
- фильтровать товары по категориям, по цене и не только;
- открывать карточку товара;
- добавлять товары в корзину;
- оформлять заказ;
- просматривать историю заказов;

## Возможности

- Каталог товаров.
- Поиск и фильтрация.
- Страница товара.
- Корзина.
- Оформление заказа.
- Авторизация и регистрация.

## Роли и доступ

В проекте предусмотрено разделение прав доступа:
- `user` — обычный пользователь, может просматривать товары, оформлять заказы, управлять своим профилем.
- `admin` — администратор, может управлять товарами, категориями, заказами и пользователями.

## Технологии

- Python 3.12
- FastAPI
- Pydantic
- PyJWT
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Docker

## Структура проекта

```bash
ecommerce-backend/
├── alembic/
├── app/
├── tests/
├──.dockerignore
├── .env
├── .env.example
├──.gitignore
├── alembic.ini 
├── docker-compose.yml 
├── Dockerfile
├── pytest.ini
├── README.md
└── requirements.txt

```

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Farhad-IT/E-commerce.git
```

2. Перейдите в папку проекта:
```bash
cd E-commerce
```

3. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Создайте файл `.env` на основе `.env.example`.

## Запуск проекта

```bash
uvicorn app.main:app --reload
```

### Через Docker
```bash
docker compose up --build
```
Если хотите запустить в фоновом режиме:
```bash
docker compose up --build -d
```

Ссылка на документацию: [Swagger UI](http://localhost:8000/docs)

## API Endpoints

### Auth
- `POST /auth/registration`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/user/logout`

### User
- `GET /product` - просмотр списка товаров.
- `GET /product/{product_id}` - просмотр карточки товара.
- `GET /category` - просмотр списка категорий.
- `GET /category/{category_id}` - просмотр отдельной категории.
- `POST /cart` - создание корзины.
- `GET /cart` - просмотр корзины.
- `POST /cart/items` - добавление товаров в корзину.
- `GET /cart/items/{product_id}` - просмотр товара в корзине.
- `PATCH /cart/items/{product_id}` - изменение товара в корзине.
- `DELETE /cart/items/{item_id}` - удаление товара из корзины.
- `DELETE /cart/items` - очистка корзины.
- `GET /order` - просмотр всех заказов.
- `GET /order/{order_id}/order_items` - просмотр товаров в заказе.
- `POST /order/checkout` - оформление заказа.
- `PATCH /order/{order_id}/pay` - оплата заказа.
- `PATCH /order/{order_id}/cancel` - отмена заказа.

### Admin
- `GET /users` - просмотр всех зарегистрированных пользователей.
- `PATCH /users/{user_id}` - изменение роли пользователя.
- `POST /product` - добавление товара.
- `POST /product/{product_id}/stock` - увеличение количества товаров на складе. 
- `PATCH /product/{product_id}` - изменение товара.
- `DELETE /product/{product_id}` - удалить товар.
- `POST /category` - добавление категории.
- `PATCH /category/{category_id}` - изменение категории. 
- `DELETE /category/{category_id}` - удаление категории.

## Тестирование

```bash
pytest
```

