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
