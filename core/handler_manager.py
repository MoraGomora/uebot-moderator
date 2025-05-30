from pyrogram import filters
from pyrogram.handlers import MessageHandler

from handlers.filters import check_access_control, is_admin, is_chat_allowed
from enums import CommandAccessLevel

async def register_handlers(client):
    from handlers.personal import test
    from handlers.personal import type
    from handlers.personal import flip

    from handlers.public import group_commands

    from .plugin._initializer import _PluginCommandInializer

    # ---------------- Initialize the command register ----------------
    command_register = _PluginCommandInializer()
    # ----------------- Register all handlers -----------------
    command_register._register_handlers(client)

    # ---------------- REGISTER USER COMMANDS ----------------
    client.add_handler(MessageHandler(test.test, filters.command("test", prefixes=".") & filters.me & check_access_control(CommandAccessLevel.PRIVATE)))
    client.add_handler(MessageHandler(type.type, filters.command("type", prefixes=".") & filters.me & check_access_control(CommandAccessLevel.USER)))
    client.add_handler(MessageHandler(flip.flip, filters.command("flip", prefixes=".") & filters.me & check_access_control(CommandAccessLevel.USER)))

    # ----------------- REGISTER PUBLIC COMMANDS -----------------
    client.add_handler(MessageHandler(group_commands.message_data, filters.command("messageinfo", prefixes=".") & is_chat_allowed & check_access_control(CommandAccessLevel.PUBLIC)))
    client.add_handler(MessageHandler(group_commands.user_info, filters.command("userinfo", prefixes=".") & is_chat_allowed & check_access_control(CommandAccessLevel.PUBLIC)))
    client.add_handler(MessageHandler(group_commands.tester, is_chat_allowed))
    client.add_handler(MessageHandler(group_commands.set_chat_allowed, filters.command("allow", prefixes=".") & check_access_control(CommandAccessLevel.PRIVATE) & is_admin))
    # client.add_handler(MessageHandler(group_commands.restrict_process, check_access_control(CommandAccessLevel.PUBLIC) & is_admin))
    # client.add_handler(MessageHandler(group_commands.unrestrict_process, filters.command("unrestrict", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_admin))
