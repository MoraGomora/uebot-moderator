import asyncio

from pyrogram import idle

from core.client_manager import *
from core.plugin_loader import PluginLoader
from logger import Log

log = Log("userbot-moderator")
log.getLogger().setLevel("DEBUG")
log.write_logs_to_file()

async def main():
    log.getLogger().info("Loading plugins...")
    loader = PluginLoader()
    loader.load_plugin()

    log.getLogger().info("Starting Userbot Moderator...")
    await start_new_session("test1")

    await idle()


if __name__ == "__main__":
    try:
        log.getLogger().info("Running bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        log.getLogger().info("Stopping all clients...")
        asyncio.run(stop_all_clients())