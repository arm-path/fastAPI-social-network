import io
import os
from typing import AsyncGenerator

from PIL import Image
from fastapi import UploadFile, Depends

from src.models.sessions import get_async_session
from src.routers.user_router import sign_in_user
from src.schemas.user_schema import JWTToken
from src.services.user_service import UserService


class UploadFileService:
    @classmethod
    async def check_image(cls, uploaded_file: UploadFile, max_size: tuple = None) -> bytes:
        if not uploaded_file.content_type in ['image/jpeg', 'image/png', 'image/svg']:
            raise HTTPException(status_code=400, detail={'status': 400, 'data': {'errors': ['File must be an image']}})

        content = await uploaded_file.read()
        bytes_image = io.BytesIO(content)
        image = Image.open(bytes_image)
        max_size = max_size if len(max_size) == 2 else None
        max_size = image.size if max_size is None else max_size
        image.thumbnail(max_size)
        return image

    @classmethod
    async def upload_image(cls, uploaded_file: UploadFile, dir1: str, dir2: str, max_size: tuple = None) -> str:
        static_directory = f"static/{dir1}/{dir2}"
        os.makedirs(static_directory, exist_ok=True)
        image = await cls.check_image(uploaded_file, max_size)
        image.save(f'{static_directory}/{uploaded_file.filename}')
        return f'{static_directory}/{uploaded_file.filename}'


class SignInData:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class GetCurrentUserService:
    def __init__(self, service_user: UserService = Depends(UserService),
                 session: AsyncGenerator = Depends(get_async_session)):
        self.service_user = service_user
        self.session = session

    async def get_token(self, username, password) -> JWTToken:
        return await sign_in_user(
            data_user=SignInData(username=username, password=password),
            session=self.session,
            services=self.service_user
        )

    async def get_current_user(self, token):
        return await UserService.get_jwt_user(token['access_token'])
