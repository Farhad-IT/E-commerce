from app.auth.auth_service import AuthService
from app.db.session import SessionDep

from app.categories.category_service import CategoryService
from app.order.order_service import OrderService
from app.product.product_service import ProductService
from app.cart.cart_service import CartService
from app.balance.balance_service import BalanceService

def get_category_service(db: SessionDep):
    """Функция для иньекции зависемости CategoryService"""
    return CategoryService(db)

def get_product_service(db: SessionDep):
    """Функция для иньекции зависемости ProductService"""
    return ProductService(db)

def get_cart_service(db: SessionDep):
    """Функция для иньекции зависемости CartService"""
    return CartService(db)

def get_order_service(db: SessionDep):
    """Функция для иньекции зависемости OrderService"""
    return OrderService(db)

def get_balance_service(db: SessionDep):
    """Функция для иньекции зависемости BalanceService"""
    return BalanceService(db)

def get_auth_service(db: SessionDep):
    """Функция для иньекции зависемости AuthService"""
    return AuthService(db)
