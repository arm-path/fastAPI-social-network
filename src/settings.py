from pydantic import BaseSettings
from fastapi.templating import Jinja2Templates

from src.environment import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, JWT_USER_SECRET


class Settings(BaseSettings):
    database: dict = {
        'DB_HOST': DB_HOST,
        'DB_PORT': DB_PORT,
        'DB_USER': DB_USER,
        'DB_PASSWORD': DB_PASSWORD,
        'DB_NAME': DB_NAME,
        'DATABASE_URL': f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    }
    security: dict = {
        'jwt_secret': JWT_USER_SECRET,
        'jwt_type': 'bearer',
        'jwt_lifetime': 3600,
        'jwt_algorithm': 'HS256'
    }
    messages: dict = {
        'validation': {
            'PASSWORD': 'The length of the password is preferably at least 8 characters, '
                        'the presence of characters in both cases and numbers is required',
            'USERNAME_UNIQUE': 'This username is already in use!',
            'AUTHORIZATION': 'username or password is incorrect!'
        }
    }


settings = Settings()
templates = Jinja2Templates(directory='templates')
