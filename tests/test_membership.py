from .fixtures import *
from httpx import AsyncClient


async def test_user_channel(ac: AsyncClient, channel_owner, get_user):
    response = await ac.post("/membership/add/", headers=channel_owner['headers'],
                             json={"channel_id": channel_owner['channel_id'],
                                   'user_id': get_user['user_id']})
    assert response.status_code == 201

    response = await ac.delete(f"/membership/delete?channel_id={channel_owner['channel_id']}&user_id={get_user['user_id']}", headers=channel_owner['headers'])
    assert response.status_code == 200



async def test_already_user_channel(ac: AsyncClient, channel_owner, channel_user):
    response = await ac.post("/membership/add/", headers=channel_owner['headers'],
                             json={"channel_id": channel_owner['channel_id'],
                                   'user_id': channel_user['user_id']})
    assert response.status_code == 400
    assert response.json() == {'detail': 'User is already a member of the channel'}
