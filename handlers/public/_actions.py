from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta

from pyrogram import Client

from .group import restrict, ban, message
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("ModerationActions")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
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

        self.restrict = restrict.RestrictActions(client)
        self.ban = ban.BanActions(client)
        self.message = message.MessageActions(client)

    async def apply_decision(
        self,
        chat_id: int,
        user_id: int,
        decision: ModDecision
    ) -> bool:
        try:
            if decision.action == ModAction.NONE:
                _log.getLogger().debug(f"No action taken for user {user_id} in chat {chat_id}. Reason: {decision.reason}")
                return True

            if decision.action == ModAction.MUTE:
                until_date = None
                if decision.duration:
                    until_date = datetime.now() + timedelta(seconds=decision.duration)

                _log.getLogger().debug(f"Restricting user {user_id} in chat {chat_id} for reason: {decision.reason}, until: {until_date}")

                return await self.restrict.restrict(chat_id, user_id, until_date)

            if decision.action == ModAction.BAN:
                _log.getLogger().debug(f"Banning user {user_id} in chat {chat_id} for reason: {decision.reason}")
                return await self.ban.ban_user(chat_id, user_id)

            if decision.action == ModAction.DELETE:
                _log.getLogger().debug(f"Deleting messages from user {user_id} in chat {chat_id} for reason: {decision.reason}")
                return await self.message.delete_message(chat_id, user_id)

        except Exception as e:
            _log.getLogger().error(f"Error applying moderation: {str(e)}")
            return False
