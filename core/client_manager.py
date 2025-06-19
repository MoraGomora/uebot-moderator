from pyrogram import Client

from utils.path_manager import get_session_path

from config.config import get_data
from .handler_manager import register_handlers

clients = {}

async def start_new_session(session_name: str):
    if session_name in clients:
        return
    
    api_id, api_hash = get_data()

    client = Client(name=session_name, api_id=api_id, api_hash=api_hash, workdir=get_session_path())
    await client.start()

    clients[session_name] = client

    await register_handlers(client)

async def stop_all_clients():
    for client in clients.values():
        await client.stop()