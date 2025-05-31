from datetime import datetime, timedelta

from pyrogram.enums import ChatType

from logger import Log, STANDARD_LOG_LEVEL

_log = Log("DataPattern")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

class BannedData:
    
    def to_dict(self, chat_id, data):
        # Extracting user and chat information from the data object
        _log.getLogger().debug(f"Extracting data from: {data}")
        user_id = getattr(data.user, "id", getattr(data.chat, "id", None))
        first_name = getattr(data.user, "first_name", getattr(data.chat, "title", None))
        last_name = getattr(data.user, "last_name", None)
        username = getattr(data.user, "username", getattr(data.chat, "username", None))

        is_chat = hasattr(data, "chat") and data.chat is not None
        if is_chat:
            chat_type = getattr(data.chat, "type", None)
            if chat_type == ChatType.CHANNEL:
                first_name = f"{first_name} (Channel)"

        is_bot = getattr(data.user, "is_bot", False)
        if is_bot:
            first_name = f"{first_name} (Bot)"

        # Extracting restricted_by information
        _log.getLogger().debug(f"Extracting restricted_by data")
        restricted_by = getattr(data, "restricted_by", None)

        if restricted_by is None:
            return
        
        restricted_by_user_id = getattr(restricted_by, "id", None)
        restricted_by_first_name = getattr(restricted_by, "first_name", None)
        restricted_by_last_name = getattr(restricted_by, "last_name", None)
        restricted_by_username = getattr(restricted_by, "username", None)
        restricted_by_is_bot = getattr(restricted_by, "is_bot", None)

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        _log.getLogger().debug(f"Creating data dictionary for banned user")
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "restricted_by": {
                "user_id": restricted_by_user_id,
                "first_name": restricted_by_first_name,
                "last_name": restricted_by_last_name,
                "username": restricted_by_username,
                "is_bot": restricted_by_is_bot
            },
            "created_at": created_at
        }

        _log.getLogger().debug(f"Data dictionary created: {data}")

        return data
    
    def is_dict_different(self, old: list, new: dict) -> bool:
        """
        Compare two dictionaries and return True if they are different, False otherwise.
        :param old: The first dictionary to compare.
        :param new: The second dictionary to compare.
        :return: True if the dictionaries are different, False if they are the same.
        """
        if not isinstance(old, list) or not isinstance(new, dict):
            _log.getLogger().error("Invalid data types: 'old' should be a list and 'new' should be a dictionary.")
            return False
        
        if not old or not new:
            _log.getLogger().error("One of the dictionaries is empty.")
            return False
        
        for item in old:
            if not isinstance(item, dict):
                _log.getLogger().error("One of the items in the list is not a dictionary.")
                return False
            
            if "_id" in item:
                item.pop("_id")
        
            keys1 = set(item.keys())
            keys2 = set(new.keys())
        
            if keys1.union(keys2) == keys1.intersection(keys2):
                _log.getLogger().debug("Dictionaries have the same keys")
                return False
        
        return False
    
class AllowChat:

    def to_dict(self, data):
        """
        Convert chat data to a dictionary format.
        :param chat_id: The ID of the chat.
        :param data: The data object containing chat information.
        :return: A dictionary representation of the chat data.
        """
        _log.getLogger().debug(f"Extracting data for 'allowed-chats'...")
        chat_id = getattr(data, "id", None)
        title = getattr(data, "title", None)
        username = getattr(data, "username", None)
        # chat_type = getattr(data, "type", None)
        is_scam = getattr(data, "is_scam", None)
        has_protected_content = getattr(data, "has_protected_content", None)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if getattr(data, "type", None) == ChatType.SUPERGROUP:
            chat_type = "supergroup"
        elif getattr(data, "type", None) == ChatType.GROUP:
            chat_type = "group"

        _log.getLogger().debug(f"Creating data dictionary for allowed chat")
        data_dict = {
            "chat_id": chat_id,
            "title": title,
            "username": username,
            "chat_type": chat_type,
            "is_scam": is_scam,
            "has_protected_content": has_protected_content,
            "created_at": created_at
        }

        _log.getLogger().debug(f"Data dictionary created: {data_dict}")

        return data_dict