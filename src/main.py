from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.routers.post_router import router as post_router
from src.routers.user_router import router as user_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router, prefix='/user')
app.include_router(post_router, prefix='/page')
