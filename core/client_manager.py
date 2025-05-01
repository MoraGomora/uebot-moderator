from pyrogram import Client

from utils.path_manager import get_session_path

from config.instances import INSTANCES
from config.config import get_data

clients = []

async def init_clients():
    api_id, api_hash = get_data()

    for instance in INSTANCES:
        client = Client(
            name=instance["name"],
            api_id=api_id,
            api_hash=api_hash,
            workdir=get_session_path()
        )
        clients.append(client)