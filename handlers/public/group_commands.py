from pyrogram.errors import UserNotMutualContact

from utils.messages import format_message_info, format_user_info

async def message_data(client, msg):
    try:
        reply_message = getattr(msg, "reply_to_message", None)

        if reply_message is None:
            return
        
        await client.send_message(msg.chat.id, format_message_info(reply_message))
    except Exception as e:
        print(f"Something was happened: {e}")

def find_photo_by_unique_id(photos, target_unique_id: str):
    for photo in photos:
        if photo.file_unique_id == target_unique_id:
            return photo
    return None

async def user_info(client, msg):
    reply_message = getattr(msg, "reply_to_message", None)
    
    if reply_message is None:
        await msg.reply("For this feature to work, you need to mark any message of the person you are interested in")
        return

    try:
        user = await client.get_users(reply_message.from_user.id)
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    caption = format_user_info(user)

    try:
        current_photo = getattr(user, "photo", None)

        if current_photo is None:
            await client.send_message(msg.chat.id, caption)
            return

        photos = [p async for p in client.get_chat_photos(user.id)]
        photo = find_photo_by_unique_id(photos, current_photo.big_photo_unique_id)
            
        await client.send_photo(msg.chat.id, photo.file_id, caption=caption)
    except UserNotMutualContact:
        pass
    except Exception as e:
        print(f"[!] Error loading photo: {e}")
