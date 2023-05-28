from datetime import datetime, timedelta
from typing import Annotated
from typing import AsyncGenerator

from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

from src.models.sessions import async_session
from src.models.tables import User
from src.schemas.user_schema import CreateUserSchema, TokenUserSchema, JWTToken, JWTTokenPayload
from src.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/sign-in/')


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenUserSchema:
    return await UserService.get_jwt_user(token)


class UserService:
    @classmethod
    def create_hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def check_password(cls, plain_password: str, hash_password: str) -> bool:
        return bcrypt.verify(plain_password, hash_password)

    @classmethod
    def create_jwt_token(cls, user) -> JWTToken:
        data = {
            'sub': str(user.id),
            'username': user.username,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(seconds=settings.security['jwt_lifetime'])
        }
        access_token = jwt.encode(data, settings.security['jwt_secret'], algorithm=settings.security['jwt_algorithm'])
        return {'access_token': access_token, 'token_type': settings.security['jwt_type']}

    @classmethod
    def check_jwt_token(cls, token: str) -> JWTTokenPayload:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        try:
            payload = jwt.decode(token, settings.security['jwt_secret'],
                                 algorithms=[settings.security['jwt_algorithm']])
        except JWTError:
            raise credentials_exception
        return payload

    @classmethod
    async def get_jwt_user(cls, token: str) -> TokenUserSchema:
        payload = cls.check_jwt_token(token)
        async with async_session() as session:
            user_id = int(payload['sub'])
            user = await session.execute(
                select(User).options(
                    load_only(User.id, User.username, User.email, User.first_name, User.last_name, User.active)
                ).filter(User.id == user_id))
            user_db = user.scalars().one()
        return {'id': user_db.id, 'email': user_db.email, 'username': user_db.username}

    async def create_user(self, session: AsyncGenerator, data_user: CreateUserSchema):
        data_user = data_user.dict()
        data_user['password'] = self.create_hash_password(data_user['password'])
        try:
            await session.execute(insert(User).values(**data_user))
        except IntegrityError as errorData:
            exception_detail = {'data': {'errors': [settings.messages['validation']['USERNAME_UNIQUE']]}}
            if errorData.orig.__cause__.__class__ == UniqueViolationError:
                raise HTTPException(status_code=400, detail=exception_detail)
            print('-->', errorData)
        except Exception as errorData:
            print('-->', errorData)
        await session.commit()

    async def authorization_user(self, session: AsyncGenerator, data_user: OAuth2PasswordRequestForm):
        user = await session.execute(select(User).filter(User.username == data_user.username))
        exception_detail = {'data': {'errors': [settings.messages['validation']['AUTHORIZATION']]}}
        user_db = {'password': ''}
        try:
            user_db = user.scalars().all()[0]
        except IndexError as errorData:
            raise HTTPException(status_code=400, detail=exception_detail)
        except Exception as errorData:
            print('-->', errorData)
        if not self.check_password(data_user.password, user_db.password):
            raise HTTPException(status_code=400, detail=exception_detail)

        return self.create_jwt_token(user_db)
