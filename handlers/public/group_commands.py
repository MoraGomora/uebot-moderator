from pyrogram.types import ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter, ChatType
from pyrogram.errors import UserNotMutualContact

from utils.messages import *

from core.ai_manager import AIManager
from core.db_manager import DBManager
from ._actions import ModAction, ModDecision, ModerationActions
from ._data_pattern import BannedData, AllowChat
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("GroupCommands")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

ai = AIManager()
db_blocked = DBManager('moderator-db', 'banned-users')
db_chat_allowed = DBManager('moderator-db', 'allowed-chats')

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


async def is_user_restricted(client, msg) -> bool:
    try:
        reply_msg = getattr(msg, "reply_to_message", None)
        user = await client.get_chat_member(msg.chat.id, reply_msg.from_user.id)

        return True if user.status == ChatMemberStatus.RESTRICTED else False
    except Exception as e:
        await client.send_message(msg.chat.id, f"Something was happened: {e}")


async def get_restricted_data(client, msg):
    try:
        reply_msg = getattr(msg, "reply_to_message", None)
        if reply_msg is None:
            await client.send_message(msg.chat.id, "Чтобы команда сработала, вам нужно ответить на любое сообщение интересующего вас пользователя.")
            return None
        if getattr(reply_msg, "sender_chat", None):
            await client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать сообщение пользователя, а не группы или канала.")
            return None

        user = await client.get_chat_member(msg.chat.id, reply_msg.from_user.id)
        if user is None:
            return None

        def get_restricted_by_user():
            return getattr(user, "restricted_by", None)
        
        def get_restricted_user_data():
            return getattr(user, "user", None)
        
        get_user_data = get_restricted_user_data()
        get_resticted_by = get_restricted_by_user()

        return get_user_data, get_resticted_by
    except Exception as e:
        await client.send_message(msg.chat.id, f"Something was happened: {e}")


async def delete_message(client, msg):
    try:
        reply_msg = getattr(msg, "reply_to_message", None)
        await client.delete_messages(msg.chat.id, reply_msg.id) # this function return a number of deleted messages
    except Exception as e:
        await client.send_message(msg.chat.id, f"Something was happened: {e}")


# async def restrict_process(client, msg):
#     reply_msg = getattr(msg, "reply_to_message", None)
#     is_restricted = await is_user_restricted(client, msg)

#     if reply_msg is None:
#         await client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать любое сообщение пользователя, которого вы хотите ограничить")
#         return
#     if reply_msg.from_user.id == msg.from_user.id:
#         await client.send_message(msg.chat.id, "ОГРАНИЧЕНИЕ: Ты не можешь ограничить сам себя.")
#         return
    
#     if not is_restricted:
#         is_restrict = await restrict(client, msg)
#         get_user_data, get_restricted_by = await get_restricted_data(client, msg)
#         message = format_user_restriction_info(get_user_data, msg.from_user, get_restricted_by, None)

#         if is_restrict:
#             await delete_message(client, msg)
#             await client.send_message(msg.chat.id, message)
#         else:
#             await client.send_message(msg.chat.id, f"Пользователь {get_user_data.first_name} уже ограничен")

async def restrict_process(client, msg):
    mod_actions = ModerationActions(client)
    reply_msg = getattr(msg, "reply_to_message", None)

    if reply_msg is None:
        await client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать любое сообщение пользователя, которого вы хотите ограничить")
        return
    if reply_msg.from_user.id == msg.from_user.id:
        await client.send_message(msg.chat.id, "ОГРАНИЧЕНИЕ: Ты не можешь ограничить сам себя.")
        return

    decision = await ai.analyze_message(msg.text)

    if decision.confidence < 0.5:
        await client.send_message(msg.chat.id, "AI не уверен в своем решении. Сообщение будет рассмотрено модерацией (пока-что это тест).")
    else:
        await mod_actions.apply_decision(
            reply_msg.chat.id,
            reply_msg.from_user.id,
            decision
        )

async def tester(client, msg):
    banned_data = BannedData()

    datas = [member async for member in client.get_chat_members(msg.chat.id, filter=ChatMembersFilter.BANNED, limit=40)]
    users = []

    db_data = await db_blocked.find_data_in_collection_by({"chat_id": msg.chat.id})

    for data in datas:
        user = banned_data.to_dict(msg.chat.id, data)
        user_id = getattr(data.user, "id", getattr(data.chat, "id", None))
        is_new = banned_data.is_dict_different(db_data, user)

        if any(d['user_id'] == user_id for d in db_data):
            _log.getLogger().debug(f"User {user_id} already exists in the database.")
            continue
            
        if is_new:
            _log.getLogger().debug(f"User {user_id} data has changed, updating in the database.")
            await db_blocked.update_many_data({"chat_id": msg.chat.id}, user)
            continue
        
        if user_id is None:
            continue

        users.append(user)

    if not users:
        return
    
    _log.getLogger().debug(f"Found {len(users)} users to insert into the database.")
    result = await db_blocked.insert_many_data(users)
    
    if result:
        _log.getLogger().debug(f"Inserted {len(users)} users into the database.")
    if len(users) == len(db_data):
        _log.getLogger().debug("All users already exist in the database.")

async def set_chat_allowed(client, msg):
    allow_chat_data = AllowChat()

    try:
        chat = await client.get_chat(msg.chat.id)
        allow_chat = allow_chat_data.to_dict(chat)
        data = await db_chat_allowed.find_data_in_collection_by({"chat_id": msg.chat.id})

        if data:
            await client.edit_message_text(msg.chat.id, msg.id, "Этот чат уже добавлен в список разрешенных.")
            return
        
        if hasattr(chat, "is_forum"):
            await client.edit_message_text(msg.chat.id, msg.id, "Форумы не поддерживаются в этой версии бота.")
            return
        
        if chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
            await client.edit_message_text(msg.chat.id, msg.id, "Эта команда работает только в группах и супергруппах.")
            return
        
        result = await db_chat_allowed.insert_one_data(allow_chat)
        if result:
            _log.getLogger().debug(f"Chat {chat.title} ({chat.id}) added to allowed chats.")
            await client.edit_message_text(msg.chat.id, msg.id, "Чат успешно добавлен в список разрешенных.")
    except Exception as e:
        await client.send_message(msg.chat.id, f"Что-то пошло не так: {e}")

async def unrestrict_process(client, msg):
    reply_msg = getattr(msg, "reply_to_message", None)
    is_restricted = await is_user_restricted(client, msg)

    if reply_msg is None:
        await client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать любое сообщение пользователя, которого вы хотите ограничить")
        return
    if reply_msg.from_user.id == msg.from_user.id:
        await client.send_message(msg.chat.id, "ОГРАНИЧЕНИЕ: Ты не можешь ограничить сам себя.")
        return
    
    if is_restricted:
        is_unrestrict = await unrestrict(client, msg)
        get_user_data, _ = await get_restricted_data(client, msg)

        if is_unrestrict:
            await client.send_message(msg.chat.id, f"С пользователя {get_user_data.first_name} сняты все ограничения")
        else:
            await client.send_message(msg.chat.id, f"Пользователь {get_user_data.first_name} не имеет никаких ограничений в этой группе")


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
        await msg.reply("Чтобы эта функция работала, вам нужно отметить любое сообщение интересующего вас человека")
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
