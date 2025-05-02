import asyncio

from core.client_manager import start_new_session, stop_all_clients

async def main():
    await start_new_session("test1")
    
    print("-------------------- BOT IS RUNNING --------------------")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(stop_all_clients())