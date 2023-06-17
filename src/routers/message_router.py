from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.exceptions import WebSocketException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.services.message_service import MessageService, ConnectionManager, \
    MessageAuxiliaryService
from src.settings import templates

router = APIRouter(tags=['messages'])


@router.post('/send')
async def send_message(user_id: int, message: str,
                       service: MessageService = Depends()):
    return await service.send_message(user_id, message)


@router.get('/get/{username}')
async def chat(username: str,
               service: MessageService = Depends()):
    return await service.chat(username)


@router.get('/with/{username}', )
async def room_chat(request: Request, username: str,
                    service: MessageAuxiliaryService = Depends()):
    token = request.cookies.get('jwt-token')
    if token is None:
        raise HTTPException(status_code=403)
    await service.get_websocket_template_user({'access_token': token})
    user = await service.get_user(username, filter_field='username')
    messages = await service.chat(username)
    return templates.TemplateResponse('messages/chat.html', {'request': request, 'username': username,
                                                             'messages': messages['messages'][username]})


manager = ConnectionManager()


@router.websocket('/ws/{username}')
async def room_chat_ws(websocket: WebSocket, username: str,
                       service: MessageAuxiliaryService = Depends()):
    token = websocket.cookies.get('jwt-token')
    if token is None:
        print('Error => routers.message_router.room_chat_ws: Cookie token not found')
        raise WebSocketException(code=403)
    await service.get_websocket_template_user({'access_token': token})
    user = await service.get_user(username, filter_field='username', ws=True)
    chat = await service.get_chat(user.id)
    chat_websocket = f'chat_{chat.id}'
    await manager.connect(websocket, chat_websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(websocket, chat_websocket, user, chat, data, service)
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_websocket)
