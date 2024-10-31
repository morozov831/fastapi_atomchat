from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.backend.db import async_session_maker
from app.backend.db_depends import get_db
from app.models import *
from app.routers.auth import get_current_user
from sqlalchemy import insert, select, update
from fastapi_cache.decorator import cache


from fastapi import WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.websockets import WebSocketDisconnect


router = APIRouter(prefix='/message', tags=['message'])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, channel_id: int, sender_id: int, message: str):
        user = await self.username(sender_id)
        await self.add_messages_to_database(channel_id, sender_id, message)
        for connection in self.active_connections:
            await connection.send_text(f'{user}: {message}')



    @staticmethod
    async def add_messages_to_database(channel_id: int, sender_id: int, message: str):
        async with async_session_maker() as session:
            ms = insert(Message).values(channel_id=channel_id, sender_id=sender_id, content=message)
            await session.execute(ms)
            await session.commit()

    @staticmethod
    async def username(user_id):
        async with async_session_maker() as session:
            user = await session.scalar(select(User).where(User.id == user_id))
            return user.username

    @staticmethod
    async def get_channel_history(channel_id: int):
        async with async_session_maker() as session:
            messages = await session.execute(select(Message).where(Message.channel_id == channel_id).order_by(Message.created_at.desc()).limit(10 ))
            return messages.scalars().all()[::-1]

    @staticmethod
    async def get_channel(channel_id: int):
        async with async_session_maker() as session:
            channel = await session.scalar(select(Channel).where(channel_id == Channel.id))
            return channel.name


    async def check_user_in_channel(self, user_id: int, channel_id: int):
        async with async_session_maker() as session:
            result = await session.execute(
                select(ChannelMember).where(ChannelMember.user_id == user_id, ChannelMember.channel_id == channel_id))
            return result.fetchone() is not None


manager = ConnectionManager()




security = HTTPBearer()

@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: int):
    await manager.connect(websocket)

    auth: HTTPAuthorizationCredentials = await security(websocket)
    token = auth.credentials

    try:
        user_data = await get_current_user(token)
        user_id = user_data.get('id')
        user_role = user_data.get('role')

        if not (user_role == 'user' and await manager.check_user_in_channel(user_id, channel_id)) and user_role != 'moderator':
            await websocket.send_text("Ошибка: Вы не являетесь участником этого канала.")
            await websocket.close()
            return
        channel = await manager.get_channel(channel_id)
        await websocket.send_text(f"Канал {channel}")

        messages = await manager.get_channel_history(channel_id)
        for msg in messages:
            username = await manager.username(msg.sender_id)
            await websocket.send_text(f'{username}: {msg.content}')
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(channel_id, user_id, data)

    except WebSocketDisconnect as err:
        manager.disconnect(websocket)
        print(err)
    except HTTPException as e:
        await websocket.send_text("Ошибка: Пользователь не существует.")
        await websocket.close()
    except Exception as e:
        await websocket.close()
        print(f"Error: {str(e)}")


@router.get("/history/{channel_id}")
@cache(expire=30)
async def get_channel_history(channel_id: int, db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)]):
    user_id = get_user.get('id')
    user_role = get_user.get('role')

    channel = await db.scalar(select(Channel).where(channel_id == Channel.id, Channel.is_active == True))
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')

    if not (user_role == 'moderator' or await manager.check_user_in_channel(user_id, channel_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this channel.")

    result = await db.execute(
        select(Message, User)
        .join(User, Message.sender_id == User.id)
        .where(Message.channel_id == channel_id)
        .order_by(Message.created_at.desc())
    )

    members = [
        {
            "username": user.username,
            "content": message.content.strip(),
            "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for message, user in result.all()
    ]

    return members