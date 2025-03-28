import uuid

from fastapi import APIRouter, Depends, Query
# from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db
from src.dependencies import get_current_user, get_current_admin
from src.accounts.models import UserModel
from src.accounts.schemas import UserDb, UserUpdate, UserCreateAdmin, UserUpdateAdmin
from src.accounts.service import UserService
from src.exceptions import ErrorResponseModel
from src import responses

router = APIRouter()


@router.get("/Me", response_model=UserDb, responses={
    401: responses.full_401
})
async def get_user_info(
        user: UserModel = Depends(get_current_user)
):
    return user


@router.put("/Update", response_model=UserDb, responses={
    401: responses.full_401,
    409: responses.username_409
})
async def update_user_info(
        data: UserUpdate,
        user: UserModel = Depends(get_current_user),
        session: AsyncSession = Depends(db.get_async_session)
):
    return await UserService.update_user(user.id, data, session)


@router.get("", response_model=list[UserDb], responses={
    401: responses.full_401,
    403: responses.full_403
})
# @cache(expire=30)
async def get_list_users_info(
        offset: int = Query(..., alias="from"),
        count: int = Query(...),
        admin: UserModel = Depends(get_current_admin),
        session: AsyncSession = Depends(db.get_async_session)
):
    return await UserService.get_list_users(offset=offset, limit=count, session=session)


@router.post("", response_model=UserDb, responses={
    401: responses.full_401,
    403: responses.full_403,
    409: responses.username_409
})
async def create_user(
        data: UserCreateAdmin,
        admin: UserModel = Depends(get_current_admin),
        session: AsyncSession = Depends(db.get_async_session)
):
    return await UserService.create_user(data, session)


@router.put("/{id}", response_model=UserDb, responses={
    401: responses.full_401,
    403: responses.full_403,
    404: responses.user_404,
    409: responses.username_409
})
async def update_user_by_id(
        id: uuid.UUID,
        data: UserUpdateAdmin,
        admin: UserModel = Depends(get_current_admin),
        session: AsyncSession = Depends(db.get_async_session)
):
    return await UserService.update_user(id, data, session)


@router.delete("/{id}", responses={
    401: responses.full_401,
    404: responses.doctor_404
})
async def delete_user_by_id(
        id: uuid.UUID,
        session: AsyncSession = Depends(db.get_async_session),
        admin: UserModel = Depends(get_current_admin),
):
    await UserService.delete_user(id, session)

