from pyrogram.enums import ChatMembersFilter

from ._data_pattern import BannedData
from core.db_manager import DBManager
from logger import Log
from constants import STANDARD_LOG_LEVEL

_log = Log("BlockedUsers")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

db = DBManager("moderator-db", "banned-users")

async def get_blocked_users(client, msg):
    banned_data = BannedData()

    datas = [member async for member in client.get_chat_members(msg.chat.id, filter=ChatMembersFilter.BANNED)]
    users = []

    db_data = await db.find_data_in_collection_by({"chat_id": msg.chat.id})

    for data in datas:
        user = banned_data.to_dict(msg.chat.id, data)
        user_id = getattr(data.user, "id", getattr(data.chat, "id", None))
        is_new = banned_data.is_dict_different(db_data, user)

        if any(d['user_id'] == user_id for d in db_data):
            _log.getLogger().debug(f"User {user_id} already exists in the database.")
            continue
            
        if is_new:
            _log.getLogger().debug(f"User {user_id} data has changed, updating in the database.")
            await db.update_many_data({"chat_id": msg.chat.id}, user)
            continue
        
        if user_id is None:
            continue

        users.append(user)

    if not users:
        return
    
    _log.getLogger().debug(f"Found {len(users)} users to insert into the database.")
    result = await db.insert_many_data(users)
    
    if result:
        _log.getLogger().debug(f"Inserted {len(users)} users into the database.")
    if len(users) == len(db_data):
        _log.getLogger().debug("All users already exist in the database.")