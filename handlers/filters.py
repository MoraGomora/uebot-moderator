from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus

from enums import CommandAccessLevel
from config.config import get_owner_id
from logger import Log, STANDARD_LOG_LEVEL

from core.db_manager import DBManager

DEVS = []

log = Log("Filters")
log.getLogger().setLevel(STANDARD_LOG_LEVEL)
log.write_logs_to_file()

def check_access_control(access_level: CommandAccessLevel):
    async def func(_, client, query):
        owner_id = int(get_owner_id())

        if getattr(query.from_user, "is_bot", False):
            log.getLogger().debug("User is a bot")
            await query.reply("Bots are not allowed to use this command.")
            return False
        if getattr(getattr(query, "forward_from", None), "is_bot", False):
            log.getLogger().debug("Forwarded message is from a bot")
            return False
            
        if query.chat.type in [ChatType.CHANNEL, ChatType.BOT]:
            return False

        if access_level == CommandAccessLevel.USER:
            if not getattr(query.from_user, "is_self", False):
                log.getLogger().debug("User is not self")
                await query.reply("To use this command, you must be logged in (authorization is not currently available)")
                return False
            return True
            
        elif access_level == CommandAccessLevel.PRIVATE:
            user_id = int(getattr(query.from_user, "id", None))

            if owner_id != user_id:
                log.getLogger().debug("User ID is not equal to owner ID")
                return False
            
            if len(DEVS) != 0:
                for dev in DEVS:
                    if not int.is_integer(dev):
                        log.getLogger().debug("Dev ID is not an integer")
                        return False
                    if user_id != dev:
                        return False
            
            return True
            
        elif access_level == CommandAccessLevel.PUBLIC:
            try:
                if query.chat.id == owner_id:
                    return False
                
                user = await client.get_chat_member(query.chat.id, owner_id)

                if user is None:
                    log.getLogger().debug("User is None")
                    return False
                if not query.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                    log.getLogger().debug("Chat type is not supergroup or group")
                    return False

                return True
            except Exception as e:
                log.getLogger().debug(f"Error in check_access_control: {e}")
                await client.send_message(query.chat.id, f"Something was happened: {e}")
                return False

    return filters.create(func)

async def is_admin(_, client, query):
    try:
        if query.chat.id == query.from_user.id:
            log.getLogger().debug("Chat ID is equal to user ID")
            return False
        
        user = await client.get_chat_member(query.chat.id, query.from_user.id)

        if user.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            log.getLogger().debug("User is admin")
            return True
    except Exception as e:
        log.getLogger().debug(f"Error in is_admin: {e}")
        await client.send_message(query.chat.id, f"Something was happened: {e}")
        return False

async def is_chat_allowed(_, client, query):
    db = DBManager("moderator-db", "allowed-chats")

    try:
        data = await db.find_data_in_collection_by({"chat_id": query.chat.id})
        chat = await client.get_chat(query.chat.id)

        if not data:
            log.getLogger().debug("Chat is not allowed")
            return False

        if chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            log.getLogger().debug("Chat type is supergroup or group")
            return True
        
        if query.chat.id == query.from_user.id:
            log.getLogger().debug("Chat ID is equal to user ID")
            return False
    except Exception as e:
        log.getLogger().debug(f"Error in is_chat_allowed: {e}")
        await client.send_message(query.chat.id, f"Something was happened: {e}")
        return False
    
async def is_user_trusted(_, client, query):
    db = DBManager("moderator-db", "trusted-users")

    try:
        reply_msg = getattr(query, "reply_to_message", None)
        if reply_msg is None or not reply_msg.from_user:
            log.getLogger().debug("Reply message is None or does not have from_user")
            return False
        
        user_id = reply_msg.from_user.id
        data = await db.find_data_in_collection_by({"chat_id": query.chat.id, "user_id": user_id})

        if not data:
            log.getLogger().debug(f"User {user_id} is not trusted in chat {query.chat.id}.")
            return False
        
        log.getLogger().debug(f"User {user_id} is trusted in chat {query.chat.id}.")
        return True
    except Exception as e:
        log.getLogger().debug(f"Error in is_user_trusted: {e}")
        await client.send_message(query.chat.id, f"Something was happened: {e}")
        return False

is_admin = filters.create(is_admin)
is_chat_allowed = filters.create(is_chat_allowed)
is_user_trusted = filters.create(is_user_trusted)