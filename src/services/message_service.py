from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.exceptions import WebSocketException
from fastapi.websockets import WebSocket
from sqlalchemy import select, insert, and_, or_
from sqlalchemy.orm import selectinload

from src.models.sessions import get_async_session
from src.models.tables import User, Chat, Messages
from src.schemas.user_schema import TokenUserSchema
from src.services.auxiliary_service import GetCurrentUserService
from src.services.user_service import get_current_user


class MessageService:
    def __init__(self, session: AsyncGenerator = Depends(get_async_session),
                 user: TokenUserSchema = Depends(get_current_user)):
        self.session = session
        self.current_user = user
        self.user_id = self.current_user['id']
        self.username = self.current_user['username']

    async def get_user(self, value_filed, filter_field='id', ws=False):
        if filter_field == 'id':
            query = select(User).filter(and_(User.id == value_filed, User.id != self.user_id))
        if filter_field == 'username':
            query = select(User).filter(and_(User.username == value_filed, User.username != self.username))
        if filter_field not in ['id', 'username']:
            raise TypeError('An unexpected argument came to the "filter_field" variable!')
        user = await self.session.execute(query)
        user = user.scalars().one_or_none()
        if user is None:
            if ws:
                print('Error => services.message_service.MessageService.get_user: Cookie token not found')
                raise WebSocketException(code=404)
            raise HTTPException(status_code=404, detail={'status': 404, 'data': {'errors': 'page not found'}})
        return user

    async def get_chat(self, user_id):
        chat = await self.session.execute(select(Chat).filter(
            or_(and_(Chat.user_chat_1_id == self.user_id, Chat.user_chat_2_id == user_id),
                and_(Chat.user_chat_1_id == user_id, Chat.user_chat_2_id == self.user_id))
        ).options(selectinload(Chat.messages)))
        chat = chat.scalars().one_or_none()
        if chat is None:
            await self.create_chat(user_id)
        return chat

    async def create_chat(self, user_id):
        await self.session.execute(insert(Chat).values(user_chat_1_id=self.user_id, user_chat_2_id=user_id))
        await self.session.commit()
        return await self.get_chat(user_id)

    async def send_message(self, user_id, message, ws=None):
        if ws is None:
            user = await self.get_user(user_id)
            chat = await self.get_chat(user_id)
        else:
            user = ws['user']
            chat = ws['chat']
        await self.session.execute(insert(Messages).values(
            sender_id=self.user_id, recipient_id=user_id, chat_id=chat.id, message=message
        ))
        await self.session.commit()
        return {'status': 201, 'data': {'username': 'user.username', 'message': message}}

    async def build_chat(self, user, chat):
        chat_messages = []
        for message in chat.messages:
            chat_message = {'type': 'incoming' if message.sender_id == user.id else 'outgoing',
                            'message': message.message, 'created': message.created}
            chat_messages.append(chat_message)
        return {user.username: chat_messages}

    async def chat(self, username):
        user = await self.get_user(username, filter_field='username')
        chat = await self.get_chat(user.id)
        chat_messages = await self.build_chat(user, chat)
        return {'messages': chat_messages}


class MessageAuxiliaryService(MessageService):
    def __init__(self, session: AsyncGenerator = Depends(get_async_session),
                 get_current_user_service: GetCurrentUserService = Depends(GetCurrentUserService)):
        self.session = session
        self.get_current_user_service = get_current_user_service
        self.current_user = None
        self.user_id = None
        self.username = None

    async def get_websocket_template_user(self, token):
        current_user = await self.get_current_user_service.get_current_user(token)
        self.current_user = current_user
        self.user_id = self.current_user['id']
        self.username = self.current_user['username']


class ConnectionManager:
    def __init__(self):
        self.chat_users: dict = {}

    async def connect(self, websocket: WebSocket, chat_websocket):
        await websocket.accept()
        if not chat_websocket in self.chat_users:
            self.chat_users[chat_websocket] = []
            self.chat_users[chat_websocket].append(websocket)
        else:
            self.chat_users[chat_websocket].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_websocket):
        if chat_websocket in self.chat_users:
            self.chat_users[chat_websocket].remove(websocket)

    async def broadcast(self, websocket: WebSocket, chat_websocket, user, chat, message: str,
                        service: MessageAuxiliaryService):
        await service.send_message(user.id, message, ws={'user': user, 'chat': chat})
        if chat_websocket in self.chat_users:
            for connection in self.chat_users[chat_websocket]:
                if connection == websocket:
                    await connection.send_json({'user': 'i', 'message': message})
                else:
                    await connection.send_json({'user': 'companion', 'message': message})
