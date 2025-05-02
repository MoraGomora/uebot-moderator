from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def register_handlers(client):
    from handlers.personal import test
    from handlers.personal import type
    from handlers.personal import flip

    from handlers.public import group_commands

    # ---------------- REGISTER PERSONAL COMMANDS ----------------
    client.add_handler(MessageHandler(test.test, filters.command("test", prefixes=".") & filters.me))
    client.add_handler(MessageHandler(type.type, filters.command("type", prefixes=".") & filters.me))
    client.add_handler(MessageHandler(flip.flip, filters.command("flip", prefixes=".") & filters.me))

    # ----------------- REGISTER PUBLIC COMMANDS -----------------
    client.add_handler(MessageHandler(group_commands.message_data, filters.command("messageinfo", prefixes=".") & filters.me))