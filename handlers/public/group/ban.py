from logger import Log, STANDARD_LOG_LEVEL

_log = Log("BanActions")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

class BanActions:

    def __init__(self, client):
        """Initialize the BanActions class with a client instance.
        :param client: The client instance to interact with the Telegram API.
        """

        self.client = client

    async def _ban_user(self, chat_id, user_id) -> bool:
        try:
            _log.getLogger().debug(f"Banning user {user_id} from chat {chat_id}")
            data = await self.client.ban_chat_member(chat_id, user_id)

            if not data:
                _log.getLogger().error(f"Failed to ban user {user_id} from chat {chat_id}")
                return False
            
            _log.getLogger().debug(f"User {user_id} has been banned from chat {chat_id}")
            
            return True
        except Exception as e:
            _log.getLogger().error(f"Something went wrong while banning user {user_id} in chat {chat_id}: {e}")
            await self.client.send_message(chat_id, f"Something was happened: {e}")