from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.routers.post_router import router as post_router
from src.routers.user_router import router as user_router
from src.routers.profile_router import router as profile_router
from src.routers.message_router import router as message_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router, prefix='/user')
app.include_router(post_router, prefix='/page')
app.include_router(profile_router, prefix='/profile')
app.include_router(message_router, prefix='/chat')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000', 'http://localhost:7000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
