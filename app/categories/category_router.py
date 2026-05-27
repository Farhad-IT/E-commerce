from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import require_role, get_current_user
from app.api.dependencies import get_category_service
from app.categories.category_schemas import CategoryCreateSchema, CategoryUpdateSchema, CategorySchema
from app.categories.category_service import CategoryService

router = APIRouter(prefix="/category", tags=["category"])

CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]

@router.get("", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def get_all_categories(cat_service: CategoryServiceDep) -> list[CategorySchema]:
    return await cat_service.get_all_categories()


@router.get("/{category_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def get_category_by_id(
        category_id: int,
        cat_service: CategoryServiceDep
) -> CategorySchema:
    return await cat_service.get_category_by_id(category_id=category_id)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
async def create_category(
        payload: CategoryCreateSchema,
        cat_service: CategoryServiceDep
) -> CategorySchema:
    return await cat_service.create_category(create_category=payload)


@router.patch("/{category_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(require_role("admin"))])
async def update_category(
        category_id: int,
        payload: CategoryUpdateSchema,
        cat_service: CategoryServiceDep
) -> CategorySchema:
    return await cat_service.update_category(category_id=category_id, update_category=payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_category(
        category_id: int,
        cat_service: CategoryServiceDep
) -> None:
    return await cat_service.delete_category(category_id=category_id)

