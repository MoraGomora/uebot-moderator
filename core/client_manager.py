import asyncio

from pyrogram import Client

from utils.path_manager import get_session_path

from config.config import get_data
from .handler_manager import register_handlers

clients = {}
queues = {}

# async def process_queue(session_name):
#     queue = queues[session_name]
#     while True:
#         msg, command_func = await queue.get()
#         try:
#             await command_func(msg)
#         except Exception as e:
#             await msg.reply(f"Ошибка: {e}")
#         queue.task_done()

async def start_new_session(session_name: str):
    if session_name in clients:
        return
    
    api_id, api_hash = get_data()

    client = Client(name=session_name, api_id=api_id, api_hash=api_hash, workdir=get_session_path())
    await client.start()

    clients[session_name] = client
    queues[session_name] = asyncio.Queue()

    # asyncio.create_task(process_queue(session_name))
    await register_handlers(client)

async def stop_all_clients():
    for client in clients.values():
        await client.stop()