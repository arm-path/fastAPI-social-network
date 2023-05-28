import io
import os
from typing import AsyncGenerator

from PIL import Image
from fastapi import HTTPException, Depends
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import load_only, selectinload

from src.models.sessions import get_async_session
from src.models.tables import Post, User
from src.schemas.post_schema import PostSchema, SortedPostSchema
from src.schemas.user_schema import TokenUserSchema
from src.services.user_service import get_current_user


class PostService:
    def __init__(self,
                 current_user: TokenUserSchema = Depends(get_current_user),
                 session: AsyncGenerator = Depends(get_async_session)):
        self.current_user = current_user
        self.user_id = self.current_user['id']
        self.username = self.current_user['username']
        self.session = session

    async def get_post(self, id_post: int):
        post = await self.session.execute(select(Post)
                                          .filter(Post.id == id_post, Post.user_id == self.user_id))
        post = post.scalars().one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail={'status': 404, 'data': {'messages': ["Item not found"]}})
        return post

    async def get_posts(self) -> PostSchema:
        try:
            posts = await self.session.execute(select(Post)
                                               .filter(Post.user_id == self.user_id)
                                               .options(load_only(Post.id, Post.image_path, Post.text, Post.created)))
            posts = posts.scalars().all()
        except Exception as errData:
            print('PostService.get_posts -> ', errData)
        return posts if 'posts' in locals() else []

    async def query_filter_user(self, filter_user: str, query_sql=None):
        try:
            user = await self.session.execute(select(User)
                                              .filter(User.username == filter_user))
            user_post = user.scalars().one_or_none()
        except Exception as errData:
            print('PostService.query_filter_user -> ', errData)
        if user_post:
            query_sql = select(Post) \
                .filter(Post.user_id == int(user_post.id)) \
                .options(load_only(Post.id, Post.text, Post.image_path, Post.created))
        return query_sql

    @classmethod
    def query_sorted_post(cls, sorted_create: SortedPostSchema, query_sql=None):
        if sorted_create and query_sql is not None:
            if sorted_create == 'descending':
                query_sql = query_sql.order_by(Post.created.desc())
            if sorted_create == 'ascending':
                query_sql = query_sql.order_by(Post.created)
        return query_sql

    async def get_posts_all(self, filter_user: str = None, sorted_create: SortedPostSchema = None):
        posts = []

        if filter_user:
            query_sql = await self.query_filter_user(filter_user)
        else:
            query_sql = select(Post) \
                .options(
                load_only(Post.id, Post.text, Post.image_path, Post.created),
                selectinload(Post.user)
                    .load_only(User.username))

        query_sql = self.query_sorted_post(sorted_create, query_sql)

        if query_sql is not None:
            try:
                posts = await self.session.execute(query_sql)
                posts = posts.scalars().all()
            except Exception as errData:
                print('PostService.get_posts_all -> ', errData)
        return posts

    @classmethod
    async def check_image(cls, uploaded_file):
        if not uploaded_file.content_type in ['image/jpeg', 'image/png', 'image/svg']:
            raise HTTPException(status_code=400, detail={'status': 400, 'data': {'errors': ['File must be an image']}})

        content = await uploaded_file.read()
        bytes_image = io.BytesIO(content)
        image = Image.open(bytes_image)
        max_size = (300, 300)
        image.thumbnail(max_size)

        return image

    async def upload_image(self, uploaded_file) -> str:
        if uploaded_file is None:
            return None
        user_posts = f"static/user_posts/{self.current_user['username']}"
        os.makedirs(user_posts, exist_ok=True)
        image = await self.check_image(uploaded_file)
        image.save(f'{user_posts}/{uploaded_file.filename}')
        return f'{user_posts}/{uploaded_file.filename}'

    async def create_post(self, text, uploaded_file):
        image_path = await self.upload_image(uploaded_file)
        try:
            user_id = int(self.current_user['id'])
            post = await self.session.execute(insert(Post).
                                              values(text=text, user_id=user_id, image_path=image_path)
                                              .returning(Post))
        except Exception as errData:
            print('PostService.create_post -> ', errData)
        await self.session.commit()
        post = post.scalars().one()
        post = {'id': post.id, 'text': post.text, 'image_path': post.image_path, 'created': post.created}
        return {'status': 201, 'data': {'message': 'resource created successfully', 'post': post}}

    async def update_post(self, id_post: int, text: str, image):
        post = await self.get_post(id_post)
        text = post.text if text is None else text
        if image is None:
            image = post.image_path
        else:
            image = await self.upload_image(image)
        post = await self.session.execute(
            update(Post)
                .filter(Post.id == id_post, Post.user_id == self.user_id)
                .values(text=text, image_path=image)
                .returning(Post)
        )
        await self.session.commit()
        post = post.scalars().one()
        post = {'id': post.id, 'text': post.text, 'image_path': post.image_path, 'created': post.created}
        return {'status': 204, 'data': {'message': 'resource updated successfully', 'post': post, }}

    async def delete_post(self, id_post: int):
        post = await self.get_post(id_post)
        await self.session.execute(delete(Post).where(Post.id == post.id))
        post = {'id': post.id, 'text': post.text, 'image_path': post.image_path, 'created': post.created}
        await self.session.commit()
        return {'status': 202, 'data': {'message': 'resource deleted successfully', 'post': post, }}
