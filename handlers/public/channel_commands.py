from pyrogram.types import ChatPermissions
from pyrogram.enums import ChatMemberStatus

from utils.messages import format_user_restriction_info

async def restrict(client, msg) -> bool:
    try:
        reply_msg = getattr(msg, "reply_to_message", None)

        if reply_msg is None:
            return None
        
        data = await client.restrict_chat_member(msg.chat.id, reply_msg.from_user.id, ChatPermissions())

        if not data:
            return False
        return True
    except Exception as e:
        await client.send_message(msg.chat.id, f"Something was happened: {e}")

async def unrestrict(client, msg):
    try:
        reply_msg = getattr(msg, "reply_to_message", None)

        if reply_msg is None:
            return None
        
        data = await client.restrict_chat_member(msg.chat.id, reply_msg.from_user.id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        ))

        if not data:
            return False
        return True
    except Exception as e:
        await client.send_message(msg.chat.id, f"Something was happened: {e}")

async def get_restricted_data(client, msg):
    try:
        reply_msg = getattr(msg, "reply_to_message", None)
        if reply_msg is None:
            await client.send_message(msg.chat.id, "For the command to work, you need to reply to any message from the user you are interested in")
            return None
        if getattr(reply_msg, "sender_chat", None):
            await client.send_message(msg.chat.id, "For the command to work, you must select a user message, not a group or channel message.")
            return None

        user = await client.get_chat_member(msg.chat.id, reply_msg.from_user.id)
        if user is None:
            return None

        def get_restricted_by_user():
            return getattr(user, "resticted_by", None)
        
        def get_restricted_user_data():
            return getattr(user, "user", None)
        
        def is_user_restricted() -> bool:
            return True if user.status == ChatMemberStatus.RESTRICTED else False
        
        get_resticted_by = get_restricted_by_user()
        get_user_data = get_restricted_user_data()
        is_restricted = is_user_restricted()

        return is_restricted, get_user_data, get_resticted_by
    except Exception as e:
        await client.send_message(msg.chat.id, f"Something was happened: {e}")

async def restrict_process(client, msg):
    reply_msg = getattr(msg, "reply_to_message", None)
    is_restricted, get_user_data, get_restricted_by = await get_restricted_data(client, msg)

    if reply_msg is None:
        await client.send_message(msg.chat.id, "For the command to work, you must select any message of the user you want to restrict")
        return
    if reply_msg.from_user.id == msg.from_user.id:
        await client.send_message(msg.chat.id, "LIMITATION: You can't limit yourself.")
        return
    
    if not is_restricted:
        is_restrict = await restrict(client, msg)
        message = format_user_restriction_info(get_user_data, msg.from_user, get_restricted_by, None)

        if is_restrict:
            await client.send_message(msg.chat.id, message)