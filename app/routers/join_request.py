from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.backend.db_depends import get_db
from app.models import *
from app.routers.auth import get_current_user
from sqlalchemy import insert, select, update

from app.schemas import JoinRequestCreate, ActionEnum, JoinRequestAction

router = APIRouter(prefix='/request', tags=['request'])


@router.get('/pending_requests/{channel_id}')
async def get_join_requests(channel_id: int, db: AsyncSession = Depends(get_db), get_user: dict = Depends(get_current_user)):
    channel = await db.scalar(select(Channel).where(Channel.id == channel_id, Channel.is_active == True))
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')
    owner_member = await db.scalar(select(ChannelMember).where(channel_id == ChannelMember.channel_id, ChannelMember.is_owner == True))
    if get_user.get('role') != 'moderator' and get_user.get('id') != owner_member.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be the channel owner or moderator.'
        )
    join_requests = await db.scalars(select(ChannelJoinRequest).where(ChannelJoinRequest.channel_id == channel_id, ChannelJoinRequest.status == 'pending'))
    if join_requests is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No join requests found for this channel')
    return join_requests.all()



@router.post('/join', status_code=status.HTTP_201_CREATED)
async def create_join_request(join_request: JoinRequestCreate, db: AsyncSession = Depends(get_db), get_user: dict = Depends(get_current_user)):
    if get_user.get('role') == 'user' or get_user.get('role') == 'moderator':
        # Проверка существования канала
        channel = await db.scalar(select(Channel).where(Channel.id == join_request.channel_id, Channel.is_active == True))
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no channel found')

        # Проверка, состоит ли пользователь уже в канале
        is_member = await db.scalar(select(ChannelMember).where(ChannelMember.channel_id == join_request.channel_id, ChannelMember.user_id == get_user['id']))
        if is_member:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User is already a member of this channel')

        # Проверка, что заявка отсутствует
        existing_request = await db.scalar(select(ChannelJoinRequest).where(ChannelJoinRequest.channel_id == join_request.channel_id, ChannelJoinRequest.user_id == get_user['id']))
        if existing_request:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Join request already exists')

        # Создание заявки на участие
        result = await db.execute(insert(ChannelJoinRequest).values(channel_id=join_request.channel_id, user_id=get_user['id']).returning(ChannelJoinRequest.id))
        await db.commit()
        join_request_id = result.scalar_one()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful', 'request_id': join_request_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

@router.get("/detail/{request_id}")
async def detail_request(request_id: int, db: Annotated[AsyncSession, Depends(get_db)], get_user: dict = Depends(get_current_user)):
    if get_user.get('role') == 'user' or get_user.get('role') == 'moderator':
        join_request = await db.scalar(select(ChannelJoinRequest).where(ChannelJoinRequest.id == request_id))
        if not join_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found")
        return join_request
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method')
@router.post("/manage", status_code=status.HTTP_200_OK)
async def manage_join_request(body: JoinRequestAction, db: Annotated[AsyncSession, Depends(get_db)], get_user: dict = Depends(get_current_user)):
    # Получаем заявку по request_id
    join_request = await db.scalar(select(ChannelJoinRequest).where(ChannelJoinRequest.id == body.request_id))
    if not join_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found")
    owner_member = await db.scalar(select(ChannelMember).where(join_request.channel_id == ChannelMember.channel_id, ChannelMember.is_owner == True))
    if get_user.get('role') != 'moderator' and get_user.get('id') != owner_member.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be the channel owner or moderator.'
        )
    if body.action == ActionEnum.accept:
        # Проверяем, не является ли пользователь уже участником канала
        existing_member = await db.scalar(select(ChannelMember).where(ChannelMember.channel_id == join_request.channel_id, ChannelMember.user_id == join_request.user_id))
        if existing_member:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User is already a member of the channel")
        # Добавляем пользователя в канал
        await db.execute(insert(ChannelMember).values(channel_id=join_request.channel_id, user_id=join_request.user_id, is_owner=False))
        # Обновляем статус заявки
        await db.execute(update(ChannelJoinRequest).where(ChannelJoinRequest.id == body.request_id).values(status="accepted"))
        await db.execute(update(Channel).where(Channel.id == join_request.channel_id).values(member_count=Channel.member_count + 1))
        await db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': "Accepted", "request_id": body.request_id}
    elif body.action == ActionEnum.decline:
        # Обновляем статус заявки на 'rejected'
        await db.execute(update(ChannelJoinRequest).where(ChannelJoinRequest.id == body.request_id).values(status="rejected"))
        await db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': "Declined", "request_id": body.request_id}