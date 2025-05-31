from pyrogram.enums import ChatType

from handlers.admin.group._data_pattern import AllowChat
from core.db_manager import DBManager
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("GroupAccess")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

db = DBManager("moderator-db", "allowed-chats")

async def allow_chat(client, msg):
    allow_chat_data = AllowChat()

    try:
        chat = await client.get_chat(msg.chat.id)
        allow_chat = allow_chat_data.to_dict(chat)
        data = await db.find_data_in_collection_by({"chat_id": msg.chat.id})

        if data:
            await client.edit_message_text(msg.chat.id, msg.id, "Этот чат уже добавлен в список разрешенных.")
            return
        
        if hasattr(chat, "is_forum"):
            await client.edit_message_text(msg.chat.id, msg.id, "Форумы не поддерживаются в этой версии бота.")
            return
        
        if chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
            await client.edit_message_text(msg.chat.id, msg.id, "Эта команда работает только в группах и супергруппах.")
            return
        
        result = await db.insert_one_data(allow_chat)
        if result:
            _log.getLogger().debug(f"Chat {chat.title} ({chat.id}) added to allowed chats.")
            await client.edit_message_text(msg.chat.id, msg.id, "Чат успешно добавлен в список разрешенных.")
    except Exception as e:
        await client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")

async def disallow_chat(client, msg):
    try:
        chat = await client.get_chat(msg.chat.id)
        data = await db.find_data_in_collection_by({"chat_id": msg.chat.id})

        if not data:
            await client.edit_message_text(msg.chat.id, msg.id, "Этот чат не найден в списке разрешенных.")
            return
        
        result = await db.delete_one_data({"chat_id": msg.chat.id})
        if result:
            _log.getLogger().debug(f"Chat {chat.title} ({chat.id}) removed from allowed chats.")
            await client.edit_message_text(msg.chat.id, msg.id, "Чат успешно удален из списка разрешенных.")
    except Exception as e:
        await client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")