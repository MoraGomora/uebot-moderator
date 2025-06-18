from core.db_manager import DBManager
from logger import Log
from constants import STANDARD_LOG_LEVEL

from .access import db

_log = Log("AutoModerationHandler")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

banned_words = DBManager("moderator-db", "banned-words")

class AutoModerationHandler:
    def __init__(self, client):
        """Initialize the AutoModerationHandler with a client instance.
        :param client: The client instance to interact with the Telegram API.
        """
        self.client = client
        _log.getLogger().debug("AutoModerationHandler initialized with DBManager")

    async def set_automoderation(self, _, msg):
        """Enable or disable automatic moderation for the chat."""
        orig_msg = msg.text.split(".automod ")[-1].strip()
        if not orig_msg:
            _log.getLogger().debug("No command provided for automod, prompting user.")
            await self.client.send_message(msg.chat.id, "Please specify whether to enable or disable automatic moderation.")
            return

        try:
            _log.getLogger().debug(f"Received command for automod: {orig_msg}")

            chat_id = msg.chat.id
            automod_status = await self._get_automod_status(chat_id)

            if automod_status is None:
                _log.getLogger().debug(f"Chat {chat_id} not found in database, initializing automod status.")
                automod_status = False
                await db.insert_one_data({"chat_id": chat_id, "automoderation": automod_status})
            
            if orig_msg.lower() in ["off", "disable", "false"]:
                if not automod_status:
                    _log.getLogger().debug(f"Automatic moderation is already disabled for chat {chat_id}.")
                    await self.client.send_message(chat_id, "Automatic moderation is already disabled.")
                    return
                else:
                    _log.getLogger().debug(f"Disabling automatic moderation for chat {chat_id}.")
                    data = await db.update_one_data({"chat_id": chat_id}, {"$set": {"automoderation": False}})

                    if data:
                        await self.client.send_message(chat_id, "Automatic moderation has been disabled.")
                        _log.getLogger().info(f"Automatic moderation disabled for chat {chat_id}.")
            elif orig_msg.lower() in ["on", "enable", "true"]:
                if automod_status:
                    _log.getLogger().debug(f"Automatic moderation is already enabled for chat {chat_id}.")
                    await self.client.send_message(chat_id, "Automatic moderation is already enabled.")
                    return
                else:
                    _log.getLogger().debug(f"Enabling automatic moderation for chat {chat_id}.")
                    data = await db.update_one_data({"chat_id": chat_id}, {"$set": {"automoderation": True}})

                    if data:
                        await self.client.send_message(chat_id, "Automatic moderation has been enabled.")
                        _log.getLogger().info(f"Automatic moderation enabled for chat {chat_id}.")
            else:
                _log.getLogger().debug(f"Invalid command for automod: {orig_msg}.")
                await self.client.send_message(chat_id, "Invalid command. Use '.automod <on/enable/true>' to enable or '.automod <off/disable/false>' to disable automatic moderation.")
                return       
        except Exception as e:
            _log.getLogger().error(f"Error in set_automoderation: {e}")
            await self.client.send_message(chat_id, f"Something went wrong: {e}")
    
    async def handle_automod(self, msg):
        """Handle automatic moderation actions based on message content."""
        try:
            if not msg.text:
                _log.getLogger().debug("Message has no text, skipping automod.")
                return
            
            # Example of checking for banned words
            banned_words = await db.get_banned_words(msg.chat.id)
            if any(word in msg.text.lower() for word in banned_words):
                await self.client.delete_messages(msg.chat.id, msg.id)
                _log.getLogger().info(f"Deleted message {msg.id} for containing banned words.")
                return
            
            # Additional automod checks can be added here
            
        except Exception as e:
            _log.getLogger().error(f"Error in handle_automod: {e}")

    async def _get_automod_status(self, chat_id):
        """Retrieve the current status of automatic moderation for a chat."""
        try:
            for chat in await db.find_data_in_collection_by({"chat_id": chat_id}):
                _log.getLogger().debug(f"Chat {chat_id} found in collection {db.collection.name}.")
                automod_status = chat.get("automoderation", None)
            _log.getLogger().debug(f"Automod status for chat {chat_id}: {automod_status}")

            return automod_status
        except Exception as e:
            _log.getLogger().error(f"Error retrieving automod status: {e}")
            return None