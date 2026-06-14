from fastapi import APIRouter, Depends, Query, status
from typing import Annotated

from app.auth.auth_dependencies import get_current_user, require_role
from app.api.dependencies import get_product_service
from app.product.product_schemas import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    QuantitySchema,
)
from app.product.product_service import ProductService
from decimal import Decimal

from app.redis.rate_limiter import rate_limiter

router = APIRouter(prefix="/product", tags=["product"])

ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
        Depends(rate_limiter(max_requests=2, window_seconds=10)),
    ],
)
async def get_all_product(
    product_services: ProductServiceDep,
    limit: int | None = 10,
    page: int | None = 1,
    min_price: Decimal | None = Query(0, ge=0),
    max_price: Decimal | None = Query(10000, le=10000),
    search: str | None = None,
    category_id: int | None = None,
    sort_by: str | None = None,
) -> list[ProductSchema]:
    return await product_services.get_all_products(
        limit=limit,
        page=page,
        min_price=min_price,
        max_price=max_price,
        title=search,
        category_id=category_id,
        sort_by=sort_by,
    )


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_product_by_id(
    product_id: int, product_services: ProductServiceDep
) -> ProductSchema:
    return await product_services.get_product_by_id(product_id=product_id)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def create_product(
    payload: ProductCreateSchema, product_services: ProductServiceDep
) -> ProductSchema:
    return await product_services.create_product(create_product=payload)


@router.post(
    "/{product_id}/stock",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role("admin"))],
)
async def add_stock_to_product(
    product_id: int, payload: QuantitySchema, product_services: ProductServiceDep
) -> ProductSchema:
    return await product_services.add_stock_to_product(
        product_id=product_id, quantity=payload
    )


@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role("admin"))],
)
async def update_product(
    product_id: int, payload: ProductUpdateSchema, product_services: ProductServiceDep
) -> ProductSchema:
    return await product_services.update_product(
        product_id=product_id, update_product=payload
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_product(product_id: int, product_services: ProductServiceDep) -> None:
    return await product_services.delete_product(product_id=product_id)
