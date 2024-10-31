#
# from .conftest import client
# from .fixtures import *
# from httpx import AsyncClient
#
#
# async def test_websocket_connection(channel_owner, get_user):
#     channel_id = channel_owner['channel_id']
#     headers = get_user['headers']
#
#     with client.websocket_connect(f'/message/ws/{channel_id}', headers=headers) as websocket:
#         response = websocket.receive_text()
#         assert "Канал" in response, f"Получено сообщение: {response}"
#         message = "Привет!"
#         websocket.send_text(message)
#         response_msg = websocket.receive_text()
#         assert response_msg == "Ваше ожидаемое сообщение"

