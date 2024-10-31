from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.backend.db_depends import get_db
from app.models import *
from app.routers.auth import get_current_user
from sqlalchemy import insert, select, update

from app.schemas import UserToChannel

router = APIRouter(prefix='/membership', tags=['membership'])

@router.post('/add', status_code=status.HTTP_201_CREATED)
async def add_user_channel(db: Annotated[AsyncSession, Depends(get_db)], body: UserToChannel, get_user: Annotated[dict, Depends(get_current_user)]):
    # Проверка существования канала
    channel = await db.scalar(select(Channel).where(body.channel_id == Channel.id, Channel.is_active == True))
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')
    # Проверка прав доступа
    owner_member = await db.scalar(select(ChannelMember).where(body.channel_id == ChannelMember.channel_id, ChannelMember.is_owner == True))
    if get_user.get('role') != 'moderator' and get_user.get('id') != owner_member.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You must be the channel owner or moderator.'
            )
    # Проверка существования пользователя
    existing_user = await db.scalar(select(User).where(User.id == body.user_id, User.is_active == True))
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    # Проверка, что пользователь не является уже участником канала
    existing_user_channel = await db.scalar(select(ChannelMember).where(ChannelMember.channel_id == body.channel_id, ChannelMember.user_id == body.user_id))
    if existing_user_channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User is already a member of the channel'
        )
    # Добавление пользователя в канал
    await db.execute(insert(ChannelMember).values(channel_id=body.channel_id, user_id=body.user_id, is_owner=False))
    await db.execute(
        update(Channel)
        .where(Channel.id == body.channel_id)
        .values(member_count=Channel.member_count + 1)
    )
    await db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_user_channel(db: Annotated[AsyncSession, Depends(get_db)], channel_id: int, user_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    # Проверка существования канала
    channel = await db.scalar(select(Channel).where(channel_id == Channel.id, Channel.is_active == True))
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')
    # Проверка прав доступа
    owner_member = await db.scalar(select(ChannelMember).where(channel_id == ChannelMember.channel_id, ChannelMember.is_owner == True))
    if get_user.get('role') != 'moderator' and get_user.get('id') != owner_member.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be the channel owner or moderator.'
        )
    # Проверка существования пользователя
    existing_user = await db.scalar(select(User).where(User.id == user_id, User.is_active == True))
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    # Проверка, что пользователь является участником канала
    existing_user_channel = await db.scalar(select(ChannelMember).where(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id))
    if not existing_user_channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The user is not a member of the channel'
        )
    # Проверка, что пользователь не является владельцем канала
    if existing_user_channel.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='You cannot remove the channel owner'
        )
    # Удаление пользователя из канала
    await db.delete(existing_user_channel)
    await db.execute(update(Channel).where(Channel.id == channel_id).values(member_count=Channel.member_count - 1))
    await db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Successful'}
