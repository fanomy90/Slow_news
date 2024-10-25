from aiohttp import web
import json

async def start_task(request):
    # Получаем параметры из URL, если они есть
    task_id = request.match_info.get('task_id')
    
    # Логика обработки задачи
    response_data = {
        "status": "success",
        "task_id": task_id
    }
    
    return web.Response(text=json.dumps(response_data), content_type='application/json')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            # Обработка сообщения от клиента
            await ws.send_str(f"Message received: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            print(f'WebSocket connection closed with exception {ws.exception()}')

    return ws

app = web.Application()

# Регистрация маршрутов WebSocket
app.router.add_get('/ws/start_task/', start_task)
app.router.add_get('/ws/start_task/{task_id}/', start_task)
app.router.add_get('/ws/', websocket_handler)  # Для обработки самого WebSocket

if __name__ == '__main__':
    web.run_app(app, port=9000)