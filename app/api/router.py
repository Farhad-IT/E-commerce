from fastapi import APIRouter

from app.auth.auth_router import router as auth_router
from app.product.product_router import router as product_router
from app.categories.category_router import router as category_router
from app.cart.cart_router import router as cart_router
from app.order.order_router import router as order_router
from app.balance.balance_router import router as fake_balance_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(product_router)
router.include_router(category_router)
router.include_router(cart_router)
router.include_router(order_router)
router.include_router(fake_balance_router)



