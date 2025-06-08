from datetime import datetime

from core.db_manager import DBManager
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("TrustedUsers")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

db = DBManager("moderator-db", "trusted-users")

class TrustedUsers:

    def __init__(self, client):
        """Initialize the TrustedUsers class with a client instance.
        :param client: The client instance to interact with the Telegram API.
        """
        self.client = client

    async def add_trusted_user(self, _, msg):
        try:
            reply_msg = getattr(msg, "reply_to_message", None)
            if reply_msg is None or not reply_msg.from_user:
                await self.client.send_message(msg.chat.id, "Пожалуйста, ответьте на сообщение пользователя, которого вы хотите сделать доверенным.")
                return
            
            user_id = reply_msg.from_user.id
            username = reply_msg.from_user.username or "Нет имени"
            nickname = reply_msg.from_user.first_name or "Нет имени"
            added_by = msg.from_user.id
            added_at = datetime.now().isoformat()
            
            data = {
                "user_id": user_id,
                "added_by": added_by,
                "added_at": added_at,
                "chat_id": msg.chat.id,
                "username": username,
                "nickname": nickname
            }
            
            existing_data = await db.find_data_in_collection_by({"chat_id": msg.chat.id, "user_id": user_id})
            
            if existing_data:
                await self.client.send_message(msg.chat.id, f"Пользователь {username} уже является доверенным.")
                return
            
            result = await db.insert_one_data(data)
            if result:
                _log.getLogger().debug(f"User {username} ({user_id}) added as trusted in chat {msg.chat.id}.")
                await self.client.send_message(msg.chat.id, f"Пользователь {username} успешно добавлен в доверенные пользователи.")
        except Exception as e:
            await self.client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")

    async def remove_trusted_user(self, _, msg):
        try:
            reply_msg = getattr(msg, "reply_to_message", None)
            if reply_msg is None or not reply_msg.from_user:
                await self.client.send_message(msg.chat.id, "Пожалуйста, ответьте на сообщение пользователя, которого вы хотите удалить из доверенных.")
                return
            
            user_id = reply_msg.from_user.id
            data = await db.find_data_in_collection_by({"chat_id": msg.chat.id, "user_id": user_id})
            
            if not data:
                await self.client.send_message(msg.chat.id, "Этот пользователь не является доверенным в этом чате.")
                return
            
            result = await db.delete_one_data({"chat_id": msg.chat.id, "user_id": user_id})
            if result:
                _log.getLogger().debug(f"User {user_id} removed from trusted users in chat {msg.chat.id}.")
                await self.client.send_message(msg.chat.id, f"Пользователь {user_id} успешно удален из доверенных пользователей.")
        except Exception as e:
            await self.client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")

    async def is_user_trusted(self, _, msg):
        try:
            reply_msg = getattr(msg, "reply_to_message", None)
            if reply_msg is None or not reply_msg.from_user:
                await self.client.send_message(msg.chat.id, "Пожалуйста, ответьте на сообщение пользователя, которого вы хотите проверить.")
                return
            
            user_id = reply_msg.from_user.id
            data = await db.find_data_in_collection_by({"chat_id": msg.chat.id, "user_id": user_id})
            
            if data:
                await self.client.send_message(msg.chat.id, f"Пользователь {reply_msg.from_user.username or 'Нет имени'} является доверенным.")
            else:
                await self.client.send_message(msg.chat.id, f"Пользователь {reply_msg.from_user.username or 'Нет имени'} не является доверенным.")
        except Exception as e:
            await self.client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")

    async def clear_trusted_users(self, _, msg):
        try:
            data = await db.find_data_in_collection_by({"chat_id": msg.chat.id})
            if not data:
                await self.client.send_message(msg.chat.id, "Нет доверенных пользователей в этом чате.")
                return
            
            result = await db.delete_many_data({"chat_id": msg.chat.id})
            if result:
                _log.getLogger().debug(f"All trusted users cleared in chat {msg.chat.id}.")
                await self.client.send_message(msg.chat.id, "Все доверенные пользователи успешно удалены.")
        except Exception as e:
            await self.client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")

    async def list_trusted_users(self, _, msg):
        try:
            data = await db.find_data_in_collection_by({"chat_id": msg.chat.id})
            if not data:
                await self.client.send_message(msg.chat.id, "Нет доверенных пользователей в этом чате.")
                return
            
            trusted_users = "\n".join([f"{user['user_id']} - {user.get('username', 'Нет имени')}" for user in data])
            await self.client.send_message(msg.chat.id, f"Доверенные пользователи:\n{trusted_users}")
        except Exception as e:
            await self.client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")
