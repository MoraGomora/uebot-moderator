from pyrogram.errors import UserNotMutualContact

from utils.messages import format_user_info
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("UserInfo")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

def find_photo_by_unique_id(photos, target_unique_id: str):
    for photo in photos:
        if photo.file_unique_id == target_unique_id:
            _log.getLogger().debug(f"Found photo with unique ID: {target_unique_id}")

            return photo
        
    _log.getLogger().debug(f"Photo with unique ID {target_unique_id} not found in the list.")
    return None

async def user_info(client, msg):
    reply_message = getattr(msg, "reply_to_message", None)
    
    if reply_message is None:
        _log.getLogger().debug("Reply message is None, cannot fetch user info.")
        await msg.reply("Чтобы эта функция работала, вам нужно отметить любое сообщение интересующего вас человека")
        return

    try:
        _log.getLogger().debug(f"Fetching user info for user ID: {reply_message.from_user.id}")

        if getattr(reply_message, "sender_chat", None):
            _log.getLogger().debug("Sender chat is not a user, cannot fetch user info.")
            return
        
        user = await client.get_users(reply_message.from_user.id)

        if user:
            _log.getLogger().debug(f"User info fetched: {user.id} - {user.first_name} {user.last_name or ''}")
    
        caption = format_user_info(user)
        current_photo = getattr(user, "photo", None)

        if current_photo is None:
            _log.getLogger().debug("User has no profile photo.")
            await client.send_message(msg.chat.id, caption)
            return

        _log.getLogger().debug(f"Fetching photos for user ID: {user.id}")
        photos = [p async for p in client.get_chat_photos(user.id)]
        photo = find_photo_by_unique_id(photos, current_photo.big_photo_unique_id)
            
        _log.getLogger().debug(f"Photo found: {photo.file_id if photo else 'None'}")
        await client.send_photo(msg.chat.id, photo.file_id, caption=caption)
    except UserNotMutualContact:
        pass
    except Exception as e:
        _log.getLogger().error(f"[!] Error: {e}")