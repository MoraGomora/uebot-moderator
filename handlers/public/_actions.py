from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.types import ChatPermissions

from .group import restrict, ban, message

from logger import Log

_log = Log("ModerationActions")
_log.getLogger().setLevel("DEBUG")
_log.write_logs_to_file()

class ModAction(Enum):
    NONE = "none"
    MUTE = "mute"
    BAN = "ban"
    DELETE = "delete"

@dataclass
class ModDecision:
    action: ModAction
    reason: str
    warning_text: Optional[str] = None
    duration: Optional[int] = None
    confidence: float = 0.0

class ModerationActions:
    def __init__(self, client: Client):
        self.client = client

    async def apply_decision(
        self,
        chat_id: int,
        user_id: int,
        decision: ModDecision
    ) -> bool:
        try:
            if decision.action == ModAction.NONE:
                return True

            if decision.action == ModAction.MUTE:
                until_date = None
                if decision.duration:
                    until_date = datetime.now() + timedelta(seconds=decision.duration)
                return await restrict.restrict(chat_id, user_id, until_date)

            if decision.action == ModAction.BAN:
                return await self._ban_user(chat_id, user_id)

            if decision.action == ModAction.DELETE:
                return await self._delete_message(chat_id, user_id)

        except Exception as e:
            _log.getLogger().error(f"Error applying moderation: {str(e)}")
            return False
        
    async def _restrict(self, chat_id, user_id, date) -> bool:
        try:
            data = await self.client.restrict_chat_member(chat_id, user_id, ChatPermissions(), date)

            if not data:
                return False
            if date:
                _log.getLogger().debug(f"User {user_id} has been restricted until {date.strftime('%Y-%m-%d %H:%M:%S')} in chat {chat_id}")
            else:
                _log.getLogger().debug(f"User {user_id} has been restricted indefinitely in chat {chat_id}")

            return True
        except Exception as e:
            _log.getLogger().error(f"Something was happened: {e}")
            await self.client.send_message(chat_id, f"Something was happened: {e}")

    async def _ban_user(self, chat_id, user_id) -> bool:
        try:
            data = await self.client.ban_chat_member(chat_id, user_id)

            if not data:
                return False
            _log.getLogger().debug(f"User {user_id} has been banned from chat {chat_id}")
            return True
        except Exception as e:
            await self.client.send_message(chat_id, f"Something was happened: {e}")

    async def _delete_message(self, chat_id, user_id) -> bool:
        try:
            user_messages = await self.client.get_chat_history(chat_id, from_user_id=user_id)
            _log.getLogger().debug(f"Found {len(user_messages)} messages from user: {user_id} in chat: {chat_id}")
            if not user_messages:
                return False
            
            for message in user_messages:
                _log.getLogger().debug(f"Deleting message: {message.id} from user: {user_id}")
                await self.client.delete_messages(chat_id, message.id)

            _log.getLogger().debug(f"All messages from user: {user_id} in chat: {chat_id} have been deleted")
            return True
        except Exception as e:
            await self.client.send_message(chat_id, f"Something was happened: {e}")

    # async def _unrestrict(client, msg):
    #     try:
    #         reply_msg = getattr(msg, "reply_to_message", None)

    #         if reply_msg is None:
    #             return None
            
    #         data = await client.restrict_chat_member(msg.chat.id, reply_msg.from_user.id, ChatPermissions(
    #             can_send_messages=True,
    #             can_send_media_messages=True,
    #             can_send_other_messages=True,
    #             can_send_polls=True,
    #             can_add_web_page_previews=True,
    #             can_change_info=True,
    #             can_invite_users=True,
    #             can_pin_messages=True
    #         ))

    #         if not data:
    #             return False
    #         return True
    #     except Exception as e:
    #         await client.send_message(msg.chat.id, f"Something was happened: {e}")