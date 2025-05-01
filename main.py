import asyncio

from pyrogram import idle

from core.client_manager import init_clients, clients

async def register_handlers(client):
    from handlers.personal import test
    from handlers.personal import type
    from handlers.personal import flip

    await test.register(client)
    await type.register(client)
    await flip.register(client)

async def main():
    await init_clients()

    for client in clients:
        await register_handlers(client)
        await client.start()

    print("BOT IS RUNNING...")

    await idle()

if __name__ == "__main__":
    asyncio.run(main())