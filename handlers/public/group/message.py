from utils.messages import format_message_info

from logger import Log, STANDARD_LOG_LEVEL

_log = Log("MessageData")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

async def message_data(client, msg):
    try:
        reply_message = getattr(msg, "reply_to_message", None)

        if reply_message is None:
            _log.getLogger().debug("Reply message is None, cannot fetch message info.")
            return
        
        _log.getLogger().debug(f"Fetching message info for message ID: {reply_message.id} in chat ID: {msg.chat.id}")
        await client.send_message(msg.chat.id, format_message_info(reply_message))
    except Exception as e:
        _log.getLogger().error(f"Something went wrong while fetching message data: {e}")

async def delete_message(client, msg):
    try:
        reply_msg = getattr(msg, "reply_to_message", None)
        _log.getLogger().debug(f"Attempting to delete message ID: {reply_msg.id} in chat ID: {msg.chat.id}")
        await client.delete_messages(msg.chat.id, reply_msg.id) # this function return a number of deleted messages
    except Exception as e:
        _log.getLogger().error(f"Something went wrong while deleting message: {e}")
        await client.send_message(msg.chat.id, f"Something was happened: {e}")

class MessageActions:

    def __init__(self, client):
        """Initialize the MessageActions class with a client instance.
        :param client: The client instance to interact with the Telegram API.
        """
        self.client = client

    async def delete_message(self, chat_id, user_id) -> bool:
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
