from fastapi import APIRouter, Depends, Form, UploadFile, File

from src.schemas.post_schema import SortedPostSchema
from src.services.post_service import PostService

router = APIRouter(tags=['posts'])


@router.get('/posts')
async def get_user_post(user: str = None,
                        created: SortedPostSchema = None,
                        services: PostService = Depends()):
    posts = await services.get_posts_all(user, created)
    return {'status': 200, 'data': {'posts': posts}}


@router.get('/my-posts')
async def get_user_post(services: PostService = Depends()):
    posts = await services.get_posts()
    return {'status': 200, 'data': {'post': posts}}


@router.get('/my-post/{id_post}')
async def get_user_post(id_post: int, services: PostService = Depends(PostService)):
    post = await services.get_post(id_post)
    return {'status': 200, 'data': {'posts': post}}


@router.post('/create-post')
async def create_post(text: str = Form(),
                      image: UploadFile = File(None),
                      services: PostService = Depends()):
    return await services.create_post(text, image)


@router.put('/update-post/{id_post}')
async def update_post(id_post: int,
                      text: str = Form(None),
                      image: UploadFile = File(None),
                      services: PostService = Depends()):
    return await services.update_post(id_post, text, image)


@router.delete('/delete-post/{id_post}')
async def delete_post(id_post: int,
                      services: PostService = Depends()):
    return await services.delete_post(id_post)
