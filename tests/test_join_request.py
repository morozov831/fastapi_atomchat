from .fixtures import *
from httpx import AsyncClient
from sqlalchemy import update


async def test_join(ac: AsyncClient, channel_owner, get_user):
    response = await ac.post("/request/join/", headers=get_user['headers'],
                             json={"channel_id": channel_owner['channel_id']})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Join request already exists'}


async def test_get_join(ac: AsyncClient, channel_owner):
    response = await ac.get(f"/request/pending_requests/{channel_owner['channel_id']}", headers=channel_owner['headers'])
    data = response.json()
    assert response.status_code == 200
    assert data[0]['status'] == 'pending'

async def test_manage_accept(ac: AsyncClient, channel_owner, get_user):
    response = await ac.post("/request/manage/", headers=channel_owner['headers'], json={
        'request_id': get_user['request_id'],
        'action': 'accept'
    })
    assert response.status_code == 200
    assert response.json()['transaction'] == 'Accepted'
    async with async_session_maker() as session:
        await session.execute(update(ChannelJoinRequest).where(get_user['user_id'] == ChannelJoinRequest.user_id).values(status='pending'))
        await session.commit()

    response = await ac.delete(
        f"/membership/delete?channel_id={channel_owner['channel_id']}&user_id={get_user['user_id']}",
        headers=channel_owner['headers'])
    assert response.status_code == 200


async def test_manage_decline(ac: AsyncClient, channel_owner, get_user):
    response = await ac.post("/request/manage/", headers=channel_owner['headers'], json={
        'request_id': get_user['request_id'],
        'action': 'decline'
    })
    assert response.status_code == 200
    assert response.json()['transaction'] == 'Declined'
    async with async_session_maker() as session:
        await session.execute(update(ChannelJoinRequest).where(get_user['user_id'] == ChannelJoinRequest.user_id).values(status='pending'))
        await session.commit()