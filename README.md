# E-Commerce REST API

A production-grade e-commerce backend built with FastAPI.

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Auth:** JWT (python-jose + bcrypt)
- **Architecture:** Router → Service → Repository pattern

## Features
- JWT Authentication (register, login)
- Products — CRUD, image upload, search, pagination
- Categories — CRUD (admin only)
- Cart — add, update, remove, clear
- Orders — place, track, admin status update
- File uploads — product images
- Background tasks — order confirmation email
- Global error handling — consistent error format
- Role-based access — admin vs customer

## Project Structure

ecommerce-api/
├── main.py                  # Entry point
├── app/
│   ├── models/              # SQLAlchemy DB models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   ├── repositories/        # DB queries
│   └── utils/               # Helpers

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register |
| POST | `/auth/login` | Login → JWT |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List with pagination + search |
| POST | `/products/` | Create (auth) |
| GET | `/products/{id}` | Get one |
| PATCH | `/products/{id}` | Update (auth) |
| DELETE | `/products/{id}` | Delete (admin) |
| POST | `/products/{id}/image` | Upload image (admin) |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cart/` | Get my cart |
| POST | `/cart/items` | Add to cart |
| PATCH | `/cart/items/{id}` | Update quantity |
| DELETE | `/cart/items/{id}` | Remove item |
| DELETE | `/cart/` | Clear cart |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders/` | Place order |
| GET | `/orders/my` | My orders |
| GET | `/orders/my/{id}` | My order detail |
| GET | `/orders/admin/all` | All orders (admin) |
| PATCH | `/orders/admin/{id}/status` | Update status (admin) |

## How to Run

### Prerequisites
- Python 3.10+
- PostgreSQL

### Setup
```bash
# Clone repo
git clone https://github.com/devanshx72/ecommerce-api
cd ecommerce-api

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your DB credentials

# Run
uvicorn main:app --reload
```

Open http://localhost:8000/docs