## BookZeno Backend

BookZeno Backend is the core service behind **BookZeno**, an online bookstore platform where users can browse books, manage carts, place orders, and complete secure payments.  
This backend exposes a RESTful API for the web frontend, handling **authentication**, **catalog management**, **cart and order workflows**, **payment integration**, **invoice / order details**, and **admin-facing operations**.

The project is built with **Django** and **Django REST Framework (DRF)** and is designed for production deployment on modern PaaS providers, with support for **PostgreSQL**, **AWS S3 media storage**, and **JWT-based authentication**.

---

## 1. Project Overview

BookZeno aims to provide a robust, scalable backend for an online bookstore, solving:

- **Product discovery**: Browse and search books by category, author, and other metadata.
- **Order management**: Add items to cart, checkout, and track order history.
- **Secure payments**: Integrate with PayPal to create and capture payments.
- **User account management**: User registration, login, password reset, and profile management.
- **Operational efficiency**: Admin-friendly endpoints to inspect and manage books, categories, and orders.

The backend is responsible for:

- Exposing **versionable, JSON-based APIs** under the `/api/` namespace.
- Applying **business rules** for cart, order, and payment flows.
- Persisting data in a **relational database** (typically PostgreSQL).
- Managing **media files** (e.g. book covers) using either local storage or **AWS S3**.
- Integrating with **email** (account verification, password reset) and **PayPal** for payments.
- Providing **OpenAPI/Swagger documentation** via DRF Spectacular.

---

## 2. Key Features

- **User authentication and authorization**
  - User registration, login, dashboard, password change, and password reset.
  - JWT-based authentication using `rest_framework_simplejwt`.
  - Email-based account activation and reset flows.

- **Book catalog management**
  - CRUD-oriented endpoints for listing and retrieving books.
  - Book details exposed via SEO-friendly slugs.
  - Category-based filtering and a dedicated book search endpoint.
  - Support for user reviews and ratings.

- **Cart system**
  - Add, remove, and decrement items in the cart.
  - Merge guest carts with authenticated user carts.
  - Persistent cart state tied to the authenticated user.

- **Order lifecycle management**
  - Checkout endpoint that converts cart content into an order.
  - Order history per user and order detail retrieval.
  - Status transitions managed via dedicated services and serializers.

- **Payment processing**
  - Integration with **PayPal** using `PAYPAL_BASE_URL`, `PAYPAL_CLIENT_ID`, and `PAYPAL_SECRET_KEY`.
  - Endpoints to create and capture payments for a given order.

- **Invoice / order details generation**
  - Structured order data accessible via API for frontend invoice rendering.
  - Timestamps and totals persisted in the orders domain.

- **Admin management features**
  - Django Admin enabled for all major models (accounts, books, categories, carts, orders).
  - Separate admin-facing API endpoints for specific tasks (e.g. `admin/books/<slug:slug>/`).

- **Secure API design**
  - Consistent success/error response wrappers via `core.utils`.
  - Authentication and permission checks enforced at the view and serializer layer.
  - CORS configuration with an allowlist for trusted frontend origins.

- **Cloud storage integration**
  - Optional integration with **AWS S3** via `django-storages` for media files.
  - Local filesystem fallback for development when S3 is not configured.

---

## 3. System Architecture

- **Framework**: Django + Django REST Framework.
- **Apps by domain**:
  - `accounts`: Authentication, profile, password management, dashboard.
  - `category`: Book categories and category-based listings.
  - `books`: Book catalog, book details, reviews, and admin book detail endpoints.
  - `carts`: Cart items, merge logic, add/remove/decrement operations.
  - `orders`: Orders, checkout, payments, and order detail/history.
  - `core`: Shared helpers such as standardized response utilities.
  - `bookzeno`: Project configuration (settings, URLs, WSGI/ASGI entrypoints).

### Request Flow

1. **Client → API Gateway**
   - All API endpoints are exposed under the `/api/` path (see `bookzeno/urls.py`).
   - Example: `GET /api/books/` or `POST /api/carts/add/`.

2. **URL Routing**
   - `bookzeno/urls.py` includes app-specific URL configurations:
     - `accounts.urls`, `category.urls`, `books.urls`, `carts.urls`, `orders.urls`.
   - API documentation endpoints are exposed via:
     - `GET /schema/` (OpenAPI schema)
     - `GET /docs/` (Swagger UI powered by DRF Spectacular)

3. **View Layer**
   - Each app uses DRF views (class-based views) to:
     - Authenticate using JWT tokens from `Authorization: Bearer <token>`.
     - Validate input using serializers.
     - Call domain-specific services (e.g. cart merging, payment creation).
     - Return standardized success/error responses from `core.utils`.

4. **Database Operations**
   - All data is stored in a relational database configured via `DATABASE_URL`.
   - Models are defined per app (`books/models.py`, `orders/models.py`, etc.).
   - Transactions and consistency are handled through Django’s ORM.

5. **Media Storage**
   - When `AWS_STORAGE_BUCKET_NAME` is set:
     - Media is stored on **AWS S3** using `storages.backends.s3boto3.S3Boto3Storage`.
     - `MEDIA_URL` points to the S3 bucket URL.
   - When not set:
     - Media files are stored locally under `MEDIA_ROOT`.

6. **Order & Payment Workflow**
   - Cart content is converted into an order during checkout.
   - Payment creation and capture are done via dedicated endpoints integrated with PayPal.
   - Order statuses and timestamps are updated according to payment events.

---

## 4. Tech Stack

- **Backend framework**:  
  - Django 6.x  
  - Django REST Framework

- **Authentication & Authorization**:  
  - JWT via `rest_framework_simplejwt`  
  - Django’s built-in auth system and password validators

- **Database**:  
  - PostgreSQL (recommended for production)  
  - Configured through `dj_database_url` and `DATABASE_URL`

- **API Documentation**:  
  - DRF Spectacular for OpenAPI schema and Swagger UI

- **Cloud Services & Storage**:  
  - AWS S3 for media storage (via `django-storages`)  
  - PayPal for payment processing

- **Static Files & Deployment**:  
  - WhiteNoise for static file serving  
  - WSGI/ASGI entrypoints in `bookzeno/wsgi.py` and `bookzeno/asgi.py`  
  - Suitable for platforms like Render, Railway, Heroku, or any WSGI-compatible server

- **Other tooling**:  
  - `python-decouple` for environment configuration  
  - `corsheaders` for CORS management

---

## 5. Folder Structure

High-level structure of the backend:

```text
bookzeno-backend/
├─ bookzeno/           # Project config (settings, URLs, WSGI/ASGI, root views)
├─ accounts/           # Auth, user profiles, dashboard, tokens, serializers, URLs
├─ books/              # Book models, serialization, views, URLs, reviews
├─ category/           # Category models, views, URLs
├─ carts/              # Cart models, services, views, URLs
├─ orders/             # Order models, services, pagination, views, URLs
├─ core/               # Shared utilities (e.g. success_response / error_response)
├─ templates/          # HTML email templates (verification, password reset, etc.)
├─ static/             # Collected static files (admin, DRF, compiled assets)
├─ manage.py           # Django management entrypoint
└─ README.md           # Project documentation (this file)
```

**Directory purposes:**

- **`bookzeno/`**: Global Django project configuration, installed apps, middleware, REST Framework setup, static/media configuration, and URL routing.
- **`accounts/`**: Everything related to user management (models, serializers, views, URLs, signals, tokens).
- **`books/`**: Book catalog domain, including detail views, search, and review-related endpoints.
- **`category/`**: Category listing and category-by-slug lookups.
- **`carts/`**: Cart and cart item domain logic, including a `services.py` module for complex cart operations.
- **`orders/`**: Checkout, orders, payments, and related services; includes pagination helpers for listing order history.
- **`core/`**: Cross-cutting utilities like standardized API responses.
- **`templates/`**: HTML templates used in email flows (e.g. account activation, password reset).
- **`static/`**: Compiled static assets used in production (served via WhiteNoise or a CDN).

---

## 6. Installation and Setup

### Prerequisites

- Python 3.10+  
- PostgreSQL (for production-like setup; SQLite can be used for local experimentation)  
- Git  

### 6.1. Clone the repository

```bash
git clone https://github.com/<your-org>/bookzeno-backend.git
cd bookzeno-backend
```

### 6.2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 6.3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.4. Create `.env` file

In the project root (`bookzeno-backend/`), create a `.env` file and configure the required environment variables (see [Environment Variables](#7-environment-variables)).

### 6.5. Apply database migrations

```bash
python manage.py migrate
```

### 6.6. Create a superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

### 6.7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`, with docs at:

- OpenAPI schema: `http://127.0.0.1:8000/schema/`
- Swagger UI: `http://127.0.0.1:8000/docs/`

---

## 7. Environment Variables

The project uses `python-decouple` and `dj_database_url` to manage configuration via environment variables.

Below is a non-exhaustive list of commonly required variables for a typical deployment:

```dotenv
# Core Django
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (PostgreSQL recommended)
DATABASE_URL=postgres://user:password@host:port/db_name

# Frontend integration
FRONTEND_URL=https://bookzeno.vercel.app

# AWS S3 (media storage)
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_REGION_NAME=your-region

# PayPal integration
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_SECRET_KEY=your-paypal-secret-key

# Email (SMTP)
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

# JWT (optional override; by default Django SECRET_KEY is used)
JWT_SECRET=your-jwt-secret

# Runtime (for some PaaS providers)
PORT=8000
```

> **Note:** Not all variables are strictly required for local development (e.g. AWS/PayPal), but they are essential for a full production setup.

---

## 8. API Endpoints Overview

The API is namespaced under `/api/`. Below is a high-level overview of core endpoints (arguments like `:slug`, `:order_number`, etc. indicate path parameters).

### 8.1. Authentication & Accounts (`accounts.urls`)

- **GET** `/api/accounts/dashboard/`  
  Returns dashboard data for the authenticated user.

- **GET/PUT** `/api/accounts/userprofile/`  
  Retrieve or update the authenticated user’s profile.

- **POST** `/api/accounts/register/`  
  Register a new user account.

- **GET** `/api/accounts/activate/<uid>/<token>/`  
  Activate a newly registered account (typically via email link).

- **POST** `/api/accounts/login/`  
  Authenticate a user and issue a JWT access/refresh token pair.

- **POST** `/api/accounts/change-password/`  
  Change password for the authenticated user.

- **POST** `/api/accounts/password-reset/`  
  Initiate a password reset email.

- **POST** `/api/accounts/password-reset-confirm/<uid>/<token>/`  
  Confirm and finalize a password reset for a user.

- **POST** `/api/accounts/token/refresh/`  
  Refresh an existing JWT access token using a valid refresh token.

### 8.2. Books (`books.urls`)

- **GET** `/api/books/`  
  List all books (with pagination).

- **GET** `/api/books/search/`  
  Search books by query parameters (e.g. title, author, category).

- **GET** `/api/books/<slug:slug>/`  
  Retrieve detailed information for a specific book.

- **POST** `/api/books/<slug:slug>/review/`  
  Submit a review for a given book (authenticated).

- **GET** `/api/books/<slug:slug>/reviews/`  
  List reviews for a given book.

- **DELETE** `/api/books/<slug:slug>/review/delete/`  
  Delete the current user’s review for a given book.

- **GET** `/api/admin/books/<slug:slug>/`  
  Admin-level book detail endpoint.

### 8.3. Categories (`category.urls`)

- **GET** `/api/category/`  
  List all categories.

- **GET** `/api/category/<slug:slug>/`  
  List books under a specific category.

### 8.4. Cart (`carts.urls`)

- **GET** `/api/carts/`  
  Retrieve the current user’s cart.

- **POST** `/api/carts/add/`  
  Add a book to the cart or increment its quantity.

- **POST** `/api/carts/merge/`  
  Merge a guest cart with the authenticated user’s cart (e.g. after login).

- **DELETE** `/api/carts/item/<int:book_id>/`  
  Remove a specific book from the cart.

- **POST** `/api/carts/item/<int:book_id>/decrement/`  
  Decrement the quantity of a specific cart item.

### 8.5. Orders & Payments (`orders.urls`)

- **GET** `/api/orders/`  
  List all orders for the authenticated user (with pagination).

- **POST** `/api/orders/checkout/`  
  Create a new order from the current cart and initiate the checkout process.

- **POST** `/api/orders/<str:order_number>/payment/create/`  
  Create a payment with PayPal for a specific order.

- **POST** `/api/orders/payment/capture/`  
  Capture a PayPal payment for an order.

- **GET** `/api/orders/<str:order_number>/`  
  Retrieve detailed information about a specific order.

---

## 9. Deployment

The backend is designed to be deployed on any **WSGI-compatible** or **ASGI-compatible** hosting platform.

### Typical Production Setup

- **Server stack**
  - `gunicorn` (or `uvicorn` for ASGI) serving `bookzeno.wsgi:application` or `bookzeno.asgi:application`.
  - Reverse proxy (e.g. Nginx) terminating TLS and forwarding requests.

- **Environment configuration**
  - Set `DEBUG=False`.
  - Configure `ALLOWED_HOSTS` with production domains.
  - Provide correct `DATABASE_URL`, AWS S3, PayPal, and email credentials.

- **Static and media**
  - Static files collected via:

    ```bash
    python manage.py collectstatic --noinput
    ```

  - Static files served via WhiteNoise or a CDN.
  - Media files stored on AWS S3 when `AWS_STORAGE_BUCKET_NAME` is configured.

- **Start command example (WSGI)**

  ```bash
  gunicorn bookzeno.wsgi:application --bind 0.0.0.0:$PORT
  ```

> **Note:** Exact deployment steps may vary by provider (Render, Railway, Heroku, Docker/Kubernetes, etc.), but the configuration principles remain the same.

---

## 10. Security Considerations

- **Password hashing**
  - Uses Django’s built-in password hashing framework and validators.

- **JWT authentication**
  - Stateless authentication using `rest_framework_simplejwt`.
  - Access tokens are short-lived and refresh tokens are used to obtain new access tokens.

- **Input validation**
  - DRF serializers validate incoming data for all major endpoints.
  - Business rules are enforced at the view/service layer.

- **CORS and cookies**
  - `CORS_ALLOWED_ORIGINS` configured to only accept requests from trusted frontends.
  - `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` are enabled for secure environments.

- **Environment variable protection**
  - Secrets (e.g. `SECRET_KEY`, database credentials, AWS keys, PayPal keys) are never committed to source control.
  - Always use `.env` files or your platform’s secret manager in production.

- **Transport security**
  - Always terminate TLS (HTTPS) at the load balancer or reverse proxy in production.

---

## 11. Future Improvements

- **Caching**
  - Introduce Redis-based caching for frequently accessed endpoints (e.g. book lists, category lists).

- **Search optimization**
  - Integrate full-text search or a dedicated search engine (e.g. Elasticsearch, OpenSearch, Meilisearch) for book discovery.

- **Microservices & modularization**
  - Extract payment, recommendation, or notification services into separate microservices if needed at scale.

- **Recommendation engine**
  - Implement personalized recommendations based on user history, ratings, and purchase behavior.

- **Rate limiting & abuse protection**
  - Add global and per-endpoint rate limiting to protect against abuse/brute-force attacks.

---

## 12. Contributing

Contributions are welcome and encouraged. To contribute:

1. **Fork** the repository on GitHub.
2. **Create a feature branch**:

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make your changes** and add tests where appropriate.
4. **Run tests and linters** to ensure quality (e.g. `python manage.py test`).
5. **Commit and push** your changes:

   ```bash
   git commit -m "Add feature XYZ"
   git push origin feature/my-new-feature
   ```

6. **Open a Pull Request** describing your changes and the motivation behind them.

Please keep PRs focused and well-documented, and follow existing code style and architecture patterns where possible.

---

## 13. License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this project in accordance with the terms of the license.

