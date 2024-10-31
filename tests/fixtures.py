import pytest
from httpx import AsyncClient
from sqlalchemy import insert, delete, select

from app.models import *
from app.routers.auth import bcrypt_context
from tests.conftest import async_session_maker


@pytest.fixture
async def add_user():
    async with async_session_maker() as session:
        existing_user_stmt = select(User).where(User.username == 'artem')
        existing_user_result = await session.execute(existing_user_stmt)
        existing_user = existing_user_result.scalar_one_or_none()

        if existing_user is None:
            await session.execute(
                insert(User).values(
                    username='artem',
                    hashed_password=bcrypt_context.hash('1234')
                )
            )
            await session.commit()
        result = await session.execute(select(User).where(User.username == 'artem'))
        user = result.scalars().first()
        yield user

@pytest.fixture
async def add_moderator():
    async with async_session_maker() as session:
        existing_user_stmt = select(User).where(User.username == 'moderator')
        existing_user_result = await session.execute(existing_user_stmt)
        existing_user = existing_user_result.scalar_one_or_none()

        if existing_user is None:
            await session.execute(
                insert(User).values(
                    username='moderator',
                    hashed_password=bcrypt_context.hash('1234'),
                    role='moderator'
                )
            )
            await session.commit()
        result = await session.execute(select(User).where(User.username == 'moderator'))
        user = result.scalars().first()
        yield user

@pytest.fixture
async def get_moderator(ac: AsyncClient, add_moderator):
    response = await ac.get("/auth/read_current_user/")
    if response.status_code == 200:
        current_user = response.json()
        if current_user.get("role") == "moderator":
            return {"Authorization": response.request.headers["Authorization"]}
    response = await ac.post("/auth/token/", data={
        "username": "moderator",
        "password": "1234"
    })

    assert response.status_code == 200, "Не удалось получить токен"
    headers = {"Authorization": f"Bearer {response.json()["access_token"]}"}
    return headers


@pytest.fixture
async def get_user(ac: AsyncClient, add_user, channel_owner):
    response = await ac.get("/auth/read_current_user/")
    if response.status_code == 200:
        current_user = response.json()
        if current_user.get("username") == "artem":
            headers = {"Authorization": response.request.headers["Authorization"]}
    else:
        response = await ac.post("/auth/token/", data={
            "username": "artem",
            "password": "1234"
        })
        headers = {"Authorization": f"Bearer {response.json()["access_token"]}"}
    user_id = add_user.id
    async with async_session_maker() as session:
        request_id = await session.scalar(select(ChannelJoinRequest.id).where(user_id == ChannelJoinRequest.user_id))
    if not request_id:
        # создание заявки на вступление в канал
        request = await ac.post('/request/join/', headers=headers, json={
            'channel_id': channel_owner['channel_id']
        })
        request_id = request.json()['request_id']
    return {"headers": headers, "user_id": user_id, "request_id": request_id}

@pytest.fixture
async def add_owner():
    async with async_session_maker() as session:
        existing_user_stmt = select(User).where(User.username == 'owner')
        existing_user_result = await session.execute(existing_user_stmt)
        existing_user = existing_user_result.scalar_one_or_none()

        if existing_user is None:
            await session.execute(
                insert(User).values(
                    username='owner',
                    hashed_password=bcrypt_context.hash('1234')
                )
            )
            await session.commit()
        result = await session.execute(select(User).where(User.username == 'owner'))
        user = result.scalars().first()
        yield user

async def get_channel_id(user_id):
    async with async_session_maker() as session:
        channel_member_stmt = select(ChannelMember.channel_id).where(ChannelMember.user_id == user_id, ChannelMember.is_owner.is_(True))
        channel_id = await session.scalar(channel_member_stmt)
    return channel_id

@pytest.fixture
async def channel_owner(ac: AsyncClient, add_owner):
    response = await ac.get("/auth/read_current_user/")
    if response.status_code == 200:
        current_user = response.json()
        if current_user.get("username") == "owner":
            headers = {"Authorization": response.request.headers["Authorization"]}
    else:
        response = await ac.post("/auth/token/", data={
            "username": "owner",
            "password": "1234"
        })
        assert response.status_code == 200, "Не удалось получить токен"
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    user_id = add_owner.id
    data = {"name": "New Channel", 'description': 'My new channel'}
    channel_id = await get_channel_id(user_id)
    if channel_id is None:
        response = await ac.post("/channel/create/", headers=headers, json=data)
        assert response.status_code == 201, f"Ошибка при создании канала: {response.status_code}, {await response.json()}"
        channel_id = await get_channel_id(user_id)
    return {"headers": headers, "channel_id": channel_id, "user_id": user_id}


@pytest.fixture
async def add_user_channel():
    async with async_session_maker() as session:
        existing_user_stmt = select(User).where(User.username == 'user_channel')
        existing_user_result = await session.execute(existing_user_stmt)
        existing_user = existing_user_result.scalar_one_or_none()

        if existing_user is None:
            await session.execute(
                insert(User).values(
                    username='user_channel',
                    hashed_password=bcrypt_context.hash('1234')
                )
            )
            await session.commit()
        result = await session.execute(select(User).where(User.username == 'user_channel'))
        user = result.scalars().first()
        yield user


@pytest.fixture
async def channel_user(ac: AsyncClient, add_user_channel, channel_owner):
    response = await ac.get("/auth/read_current_user/")
    if response.status_code == 200:
        current_user = response.json()
        if current_user.get("username") == "user_channel":
            headers = {"Authorization": response.request.headers["Authorization"]}
    else:
        response = await ac.post("/auth/token/", data={
            "username": "user_channel",
            "password": "1234"
        })
        assert response.status_code == 200, "Не удалось получить токен"
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    user_id = add_user_channel.id
    channel_id = channel_owner['channel_id']
    async with async_session_maker() as session:
        channel_member_stmt = select(ChannelMember.channel_id).where(ChannelMember.user_id == user_id)
        user = await session.scalar(channel_member_stmt)
    if not user:
        await ac.post("/membership/add/", headers=channel_owner['headers'],
                                json={"channel_id": channel_owner['channel_id'],
                                       'user_id': user_id})
    return {"headers": headers, "user_id": user_id}

