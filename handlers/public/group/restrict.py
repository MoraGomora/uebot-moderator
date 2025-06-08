from pyrogram.types import ChatPermissions
from pyrogram.enums import ChatMemberStatus

from logger import Log, STANDARD_LOG_LEVEL

_log = Log("Restrict")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

class RestrictActions:
    def __init__(self, client):
        self.client = client

    async def restrict(self, chat_id, user_id, date) -> bool:
        try:
            if not isinstance(chat_id, int) or not isinstance(user_id, int):
                raise TypeError("chat_id and user_id must be integers")
            
            _log.getLogger().debug(f"Restricting user {user_id} in chat {chat_id}")
            data = await self.client.restrict_chat_member(chat_id, user_id, ChatPermissions(), date)

            if not data:
                _log.getLogger().error(f"Failed to restrict user {user_id} in chat {chat_id}")
                return False
            
            _log.getLogger().debug(f"User {user_id} restricted successfully in chat {chat_id}")

            return True
        except Exception as e:
            _log.getLogger().error(f"Something was happened: {e}")
            await self.client.send_message(chat_id, f"Something was happened: {e}")

    async def unrestrict(client, msg):
        try:
            reply_msg = getattr(msg, "reply_to_message", None)

            if reply_msg is None:
                return None
            
            _log.getLogger().debug(f"Unrestricting user {reply_msg.from_user.id} in chat {msg.chat.id}")
            data = await client.restrict_chat_member(msg.chat.id, reply_msg.from_user.id, ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            ))

            if not data:
                return False
            
            _log.getLogger().debug(f"User {reply_msg.from_user.id} unrestricted successfully in chat {msg.chat.id}")

            return True
        except Exception as e:
            _log.getLogger().error(f"Something was happened: {e}")
            await client.send_message(msg.chat.id, f"Something was happened: {e}")

    async def is_user_restricted(client, msg) -> bool:
        try:
            reply_msg = getattr(msg, "reply_to_message", None)
            if reply_msg is None:
                return None
            
            _log.getLogger().debug(f"Checking if user {reply_msg.from_user.id} is restricted in chat {msg.chat.id}")

            user = await client.get_chat_member(msg.chat.id, reply_msg.from_user.id)

            if user is None:
                return None
            
            _log.getLogger().debug(f"User {reply_msg.from_user.id} status in chat {msg.chat.id}: {user.status}")

            return True if user.status == ChatMemberStatus.RESTRICTED else False
        except Exception as e:
            _log.getLogger().error(f"Something was happened: {e}")
            await client.send_message(msg.chat.id, f"Something was happened: {e}")
