import datetime
from typing import Optional, List

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

class MessageContext:
    """A class to represent the context of a message, including sender's name, text, and optional reply_to information."""
    
    class Message:

        def __init__(self, sender_name: str, text: str, datetime: datetime, triggered_by: str, reply_to: Optional[str] = None):
            """Initialize the MessageContext class with a client instance.
            :param client: The client instance to interact with the Telegram API.
            """
            self.sender_name = sender_name
            self.text = text
            self.reply_to = reply_to
            self.triggered_by = triggered_by
            self.datetime = datetime
    
    def __init__(self):
        self.context_lines = ["Message Context:"]

    def build_message_context(self, messages: List[Message]) -> List[str]:
        """Build a MessageContext from a message object.
        
        :param msg: The message object to build the context from.
        :return: A MessageContext instance containing the sender's name, text, message date, and optional reply_to information.
        """
        _log.getLogger().debug("Building message context from provided messages.")

        if not messages:
            _log.getLogger().debug("No messages available to build context.")
            return "\n".join(self.context_lines)
        
        if isinstance(messages, List) and not all(isinstance(msg, self.Message) for msg in messages):
            _log.getLogger().error("All items in messages must be of type Message.")
            return None

        for msg in messages:
            if msg.reply_to:
                _log.getLogger().debug(f"Message {msg.text} is a reply to {msg.reply_to}.")
                line = f"{msg.datetime} - {msg.sender_name} (replied to {msg.reply_to}): {msg.text}"
            else:
                _log.getLogger().debug(f"Message {msg.text} is not a reply.")
                line = f"{msg.datetime} - {msg.sender_name}: {msg.text}"
            self.context_lines.append(line)

        self.context_lines.append("Triggered by: " + (msg.triggered_by if msg.triggered_by else "Unknown"))
        self.context_lines.append("End of message context.")
        
        _log.getLogger().debug(f"Built message context with {len(messages)} messages.")

        return self.context_lines
    
    def to_text(self) -> str:
        """Convert the message context to a text representation.
        :return: A list of strings representing the message context.
        """
        _log.getLogger().debug("Converting message context to text representation.")
        
        if not self.context_lines:
            _log.getLogger().debug("No context lines available to convert to text.")
            return []
        
        return "\n".join(self.context_lines)
