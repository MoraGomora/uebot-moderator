import asyncio

from pyrogram import idle

from core.client_manager import start_new_session, stop_all_clients

async def main():
    await start_new_session("test1")

    print("-------------------- BOT IS RUNNING --------------------")

    await idle()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt and asyncio.exceptions.CancelledError:
        asyncio.run(stop_all_clients())