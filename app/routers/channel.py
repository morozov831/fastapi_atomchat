import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.backend.db_depends import get_db
from app.models import *
from app.routers.auth import get_current_user
from app.schemas import CreateChannel
from sqlalchemy import insert, select, update
from slugify import slugify

router = APIRouter(prefix='/channel', tags=['channel'])

@router.get('/all_channels')
@cache(expire=10)
async def get_all_channels(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('role') == 'user' or get_user.get('role') == 'moderator':
        channels = await db.scalars(select(Channel).where(Channel.is_active == True))
        if not channels:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no channel')
        return channels.all()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

@router.get('/my_channels')
@cache(expire=10)
async def get_my_channels(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('role') == 'user' or get_user.get('role') == 'moderator':
        result = await db.execute(select(Channel).join(ChannelMember, ChannelMember.channel_id == Channel.id).where(ChannelMember.user_id == get_user['id']))

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no channel')
        return result.scalars().all()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_channel(db: Annotated[AsyncSession, Depends(get_db)], create_channel: CreateChannel, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('role') == 'user' or get_user.get('role') == 'moderator':
        result = await db.execute(insert(Channel).values(name=create_channel.name, slug=slugify(create_channel.name), description=create_channel.description).returning(Channel.id))
        channel_id = result.scalar_one()
        await db.execute(insert(ChannelMember).values(channel_id=channel_id, user_id=get_user['id'], is_owner=True))
        await db.execute(update(Channel).where(Channel.id == channel_id).values(member_count=Channel.member_count + 1))
        await db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

@router.get('/detail/{channel_slug}')
async def detail_channel(db: Annotated[AsyncSession, Depends(get_db)], channel_slug: str, get_user: Annotated[dict, Depends(get_current_user)]):
    channel = await db.scalar(select(Channel).where(channel_slug == Channel.slug, Channel.is_active == True))
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')
    if get_user.get('role') == 'user' or get_user.get('role') == 'moderator':
        owner_member = await db.scalar(select(ChannelMember).where(channel.id == ChannelMember.channel_id, ChannelMember.is_owner == True))
        owner = await db.scalar(select(User).where(User.id == owner_member.user_id))
        members = await db.scalars(select(ChannelMember).where(ChannelMember.channel_id == channel.id)
        )
        member_list = []

        for member in members:
            user = await db.scalar(select(User).where(User.id == member.user_id))
            if user:
                member_list.append({
                    'id': user.id,
                    'username': user.username
                })

        return {
            'id': channel.id,
            'name': channel.name,
            'description': channel.description,
            'member_count': channel.member_count,
            'owner': owner.username,
            'members': member_list
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

@router.put('/update')
async def update_channel(db: Annotated[AsyncSession, Depends(get_db)], channel_id: int, create_channel: CreateChannel, get_user: Annotated[dict, Depends(get_current_user)]):
    channel = await db.scalar(select(Channel).where(channel_id == Channel.id, Channel.is_active == True))
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')
    owner_member = await db.scalar(select(ChannelMember).where(channel.id == ChannelMember.channel_id, ChannelMember.is_owner == True))
    if get_user.get('role') == 'moderator' or get_user.get('id') == owner_member.user_id:
            await db.execute(update(Channel).where(channel_id == Channel.id).values(name=create_channel.name, description=create_channel.description, slug=slugify(create_channel.name)))
            await db.commit()
            return {'status_code': status.HTTP_200_OK, 'transaction': 'Channel update is successful'}
    else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You must be the channel owner or moderator.'
            )

@router.delete('/delete')
async def delete_channel(db: Annotated[AsyncSession, Depends(get_db)], channel_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    channel_delete = await db.scalar(select(Channel).where(Channel.id == channel_id, Channel.is_active == True))
    if channel_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no channel found'
        )
    owner_member = await db.scalar(select(ChannelMember).where(channel_delete.id == ChannelMember.channel_id, ChannelMember.is_owner == True))
    if get_user.get('role') == 'moderator' or get_user.get('id') == owner_member.user_id:
            await db.execute(update(Channel).where(Channel.id == channel_id).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Channel delete is successful'
            }
    else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You must be the channel owner or moderator.'
            )
