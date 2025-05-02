import asyncio

from pyrogram import idle, filters
from pyrogram.handlers import MessageHandler

from core.client_manager import init_clients, clients

async def register_handlers(client):
    from handlers.personal import test
    from handlers.personal import type
    from handlers.personal import flip

    # ---------------- REGISTER PERSONAL COMMANDS ----------------
    client.add_handler(MessageHandler(test.test, filters.command("test", prefixes=".") & filters.me))
    client.add_handler(MessageHandler(type.type, filters.command("type", prefixes=".") & filters.me))
    client.add_handler(MessageHandler(flip.flip, filters.command("flip", prefixes=".") & filters.me))

async def main():
    await init_clients()

    for client in clients:
        await register_handlers(client)
        await client.start()

    print("BOT IS RUNNING...")

    await idle()

    for client in clients:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())