from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.models.sessions import get_async_session
from src.schemas.user_schema import CreateUserSchema
from src.services.user_service import UserService

router = APIRouter(tags=['users'])


@router.post('/sign-up')
async def sign_up_user(data_user: CreateUserSchema,
                       services=Depends(UserService),
                       session=Depends(get_async_session)):
    await services.create_user(session, data_user)
    return {'status': '201', 'data': {'messages': ['User successfully created!']}}


@router.post('/sign-in')
async def sign_in_user(data_user: Annotated[OAuth2PasswordRequestForm, Depends()],
                       services=Depends(UserService),
                       session=Depends(get_async_session)):
    return await services.authorization_user(session, data_user)
