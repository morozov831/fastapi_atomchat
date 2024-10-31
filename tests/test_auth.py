from .fixtures import *
from httpx import AsyncClient
from sqlalchemy import insert, delete, select, update

async def test_create_user(ac: AsyncClient):
    response = await ac.post("/auth/", json={
        "username": "test",
        "password": "test"
    })

    assert response.status_code == 201, 'Пользователь не прошел регистрацию'

async def test_unique_username(ac: AsyncClient, add_user):
    response_duplicate = await ac.post("/auth/", json={
        "username": "artem",
        "password": "1234"
    })

    assert response_duplicate.status_code == 400
    assert response_duplicate.json() == {"detail": "Username already exists"}

async def test_login(ac: AsyncClient, add_user):
    response = await ac.post("/auth/token/", data={
        "username": "artem",
        "password": "1234"
    })

    assert response.status_code == 200
    assert 'access_token' in response.json()

    response = await ac.post("/auth/token/", data={
        "username": "artem123",
        "password": "1234"
    })

    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid authentication credentials'}


async def test_block_moderator(ac: AsyncClient, get_moderator, add_user):
    headers = get_moderator
    response = await ac.delete(f"/auth/block_user?user_id={add_user.id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {'status_code': 200, 'transaction': 'User successfully blocked'}

    async with async_session_maker() as session:
        stmt = update(User).where(User.id == add_user.id).values(is_active=True)
        await session.execute(stmt)
        await session.commit()


async def test_block_user(ac: AsyncClient, get_user):
    headers = get_user['headers']
    user_id = get_user['user_id']
    response = await ac.delete(f"/auth/block_user?user_id={user_id}", headers=headers)

    assert response.status_code == 403
    assert response.json() == {'detail': 'You must be the channel moderator.'}

    async with async_session_maker() as session:
        stmt = update(User).where(User.id == user_id).values(is_active=True)
        await session.execute(stmt)
        await session.commit()

