from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine, Base
from app.routers import products, auth, categories, cart, orders
from app.models import product, user, category
from app.models import cart as cart_model
from app.models import order as order_model
from app.utils.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
import os

Base.metadata.create_all(bind=engine)

os.makedirs("uploads/products", exist_ok=True)

app = FastAPI(
    title="E-Commerce API",
    description="Complete e-commerce backend with JWT auth",
    version="1.0.0"
)

# ── Register Error Handlers ──
# Order matters — specific before general
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Welcome to E-Commerce API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "version": "1.0.0"
    }