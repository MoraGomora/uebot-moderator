from pyrogram import filters
from pyrogram.handlers import MessageHandler

from handlers.filters import *
from enums import CommandAccessLevel

async def register_handlers(client):
    from handlers.user import test
    from handlers.user import type
    from handlers.user import flip

    from handlers.public import group_commands

    from handlers.admin.group import access, blocked_users, trusted_users, automoderation
    from handlers.public.group import message, user

    from .plugin._initializer import _PluginCommandInializer

    # ---- Initialize command register and group commands ----
    command_register = _PluginCommandInializer()

    commands_group = group_commands.GroupCommands(client)
    trusted_user = trusted_users.TrustedUsers(client)
    automod_handler = automoderation.AutoModerationHandler(client)

    # ----------------- Register all handlers -----------------
    command_register._register_handlers(client)

    # ----------------- REGISTER USER COMMANDS -----------------
    client.add_handler(MessageHandler(test.test, filters.command("test", prefixes=".") & filters.me & check_access_control(CommandAccessLevel.PRIVATE)))
    client.add_handler(MessageHandler(type.type, filters.command("type", prefixes=".") & filters.me & check_access_control(CommandAccessLevel.USER)))
    client.add_handler(MessageHandler(flip.flip, filters.command("flip", prefixes=".") & filters.me & check_access_control(CommandAccessLevel.USER)))

    # ------------- REGISTER GROUP PUBLIC COMMANDS -------------
    client.add_handler(MessageHandler(message.message_data, filters.command("messageinfo", prefixes=".") & is_chat_allowed & check_access_control(CommandAccessLevel.PUBLIC)))
    client.add_handler(MessageHandler(user.user_info, filters.command("userinfo", prefixes=".") & is_chat_allowed & check_access_control(CommandAccessLevel.PUBLIC)))

    # ------------- REGISTER ADMIN PUBLIC COMMANDS -------------
    client.add_handler(MessageHandler(access.allow_chat, filters.command("allow", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_admin))
    client.add_handler(MessageHandler(access.disallow_chat, filters.command("disallow", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_admin))
    client.add_handler(MessageHandler(blocked_users.get_blocked_users, filters.command("get_blocked", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_chat_allowed & is_admin))

    client.add_handler(MessageHandler(trusted_user.add_trusted_user, filters.command("add_trusted", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_chat_allowed & is_admin))
    client.add_handler(MessageHandler(trusted_user.remove_trusted_user, filters.command("remove_trusted", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_chat_allowed & is_admin))
    # client.add_handler(MessageHandler(trusted_users.list_trusted_users, filters.command("list_trusted", prefixes=".") & check_access_control(CommandAccessLevel.PRIVATE) & is_admin & is_chat_allowed))

    client.add_handler(MessageHandler(commands_group.restrict_process, filters.command("Modxnn", prefixes="@") & is_chat_allowed))

    client.add_handler(MessageHandler(automod_handler.set_automoderation, filters.command("automod", prefixes=".") & check_access_control(CommandAccessLevel.PUBLIC) & is_chat_allowed & is_admin))
    client.add_handler(MessageHandler(commands_group.autorestrict_process, is_chat_allowed & is_automod_enabled))
