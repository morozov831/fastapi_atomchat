from .fixtures import *
from httpx import AsyncClient
from sqlalchemy import update


async def test_update(ac: AsyncClient, channel_owner):
    response = await ac.put(f'/channel/update?channel_id={channel_owner['channel_id']}', headers=channel_owner['headers'], json={"name": "Update Channel", 'description': 'Update'})
    assert response.status_code == 200

async def test_update_nochannel(ac: AsyncClient, channel_owner):
    channel_id = 4372
    response = await ac.put(f'/channel/update?channel_id={channel_id}', headers=channel_owner['headers'], json={"name": "Update Channel", 'description': 'Update'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'There is no channel found'}


async def test_delete(ac: AsyncClient, channel_owner):
    response = await ac.delete(f'/channel/delete?channel_id={channel_owner['channel_id']}', headers=channel_owner['headers'])
    assert response.status_code == 200

    async with async_session_maker() as session:
        await session.execute(update(Channel).where(Channel.id == channel_owner['channel_id']).values(is_active=True))
        await session.commit()