import asyncio
from typing import Dict, Tuple
from time import time

from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus

from enums import CommandAccessLevel
from config.config import get_owner_id
from logger import Log
from constants import STANDARD_LOG_LEVEL

from core.db_manager import DBManager

from handlers.admin.group.automoderation import AutoModerationHandler

DEVS = []

log = Log("Filters")
log.getLogger().setLevel(STANDARD_LOG_LEVEL)
log.write_logs_to_file()

# ----------------- Admin Control and Caching classes | BEGIN -----------------
class AsyncAdminCache:

    def __init__(self, ttl: int = 300):
        self._cache: Dict[Tuple[int, int], Tuple[bool, float]] = {}
        self._ttl = ttl
        self._lock = asyncio.Lock()
        self._cleanup_task = None
        self._is_running = False

    async def get(self, chat_id: int, user_id: int) -> bool | None:
        async with self._lock:
            key = (chat_id, user_id)
            if key in self._cache:
                is_admin, timestamp = self._cache[key]
                if time() - timestamp < self._ttl:
                    return is_admin
                del self._cache[key]
            return None
        
    async def set(self, chat_id: int, user_id: int, is_admin: bool):
        async with self._lock:
            self._cache[(chat_id, user_id)] = (is_admin, time())

            if len(self._cache) == 1 and not self._is_running:
                self._start_cleanup()

    async def invalidate(self, chat_id: int, user_id: int):
        async with self._lock:
            key = (chat_id, user_id)
            if key in self._cache:
                del self._cache[key]

    async def _cleanup_loop(self):
        log.getLogger().debug("_cleanup_loop is running...")

        while self._is_running and self._cache:
            try:
                await asyncio.sleep(90)
                self.cleanup()

                if not self._cache:
                    self._is_running = False
                    self._cleanup_task = None
                    log.getLogger().debug("_cleanup_loop is stopped, because cache is empty")
                    break

            except Exception as e:
                log.getLogger().error(f"Error in _cleanup_loop: {e}")
                await asyncio.sleep(5)

    def _start_cleanup(self):
        if not self._start_cleanup:
            self._start_cleanup = asyncio.create_task(self._cleanup_loop())

            if self._start_cleanup:
                self._is_running = True
                log.getLogger().debug("_start_cleanup is running...")

    def cleanup(self):
        current_time = time()
        expired = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self._ttl
        ]
        for key in expired:
            del self._cache[key]
            log.getLogger().debug(f"Remove expired entry: {key}")

class AdminControl:

    def __init__(self):
        self.admin_cache = AsyncAdminCache(250)

    async def is_admin(self, client, query):
        cached_result = await self.admin_cache.get(query.chat.id, query.from_user.id)
        if cached_result is not None:
            print(f"This is_admin value is from cache: {cached_result}")
            return cached_result

        try:
            if query.chat.id == query.from_user.id:
                log.getLogger().debug("Chat ID is equal to user ID")
                return False
            
            user = await client.get_chat_member(query.chat.id, query.from_user.id)
            is_admin = user.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            print(f"This is_admin value is new: {is_admin}")

            await self.admin_cache.set(query.chat.id, query.from_user.id, is_admin)
            
            return is_admin
        except Exception as e:
            log.getLogger().debug(f"Error in is_admin: {e}")
            await client.send_message(query.chat.id, f"Something was happened: {e}")
            return False
# ------------------ Admin Control and Caching classes | EBD ------------------

# ----------------- Other filters -----------------
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
                
                if query.chat.id == query.from_user.id:
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

async def is_chat_allowed(_, client, query):
    db = DBManager("moderator-db", "allowed-chats")

    try:
        data = await db.find_data_in_collection_by({"chat_id": query.chat.id})

        if not data:
            log.getLogger().debug("Chat is not allowed")
            return False

        if query.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
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
    
async def is_automod_enabled(_, client, query):
    automod_handler = AutoModerationHandler(client)
    try:
        if query.chat.id == query.from_user.id:
            log.getLogger().debug("Chat ID is equal to user ID")
            return False
        
        automod_status = await automod_handler._get_automod_status(query.chat.id)
        if automod_status:
            log.getLogger().debug(f"Automod is enabled in {query.chat.id} chat")
            return True
        else:
            log.getLogger().debug(f"Automod is disabled in {query.chat.id} chat")
            return False
    except Exception as e:
        log.getLogger().debug(f"Error in is_automod_enabled: {e}")
        await client.send_message(query.chat.id, f"Something was happened: {e}")
        return False

control = AdminControl()

is_admin = filters.create(control.is_admin)
is_chat_allowed = filters.create(is_chat_allowed)
is_user_trusted = filters.create(is_user_trusted)
is_automod_enabled = filters.create(is_automod_enabled)