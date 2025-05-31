from core.ai_manager import AIManager
from ._actions import ModAction, ModDecision, ModerationActions
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("GroupCommands")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

ai = AIManager()

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

# async def unrestrict_process(client, msg):
#     reply_msg = getattr(msg, "reply_to_message", None)
#     is_restricted = await is_user_restricted(client, msg)

#     if reply_msg is None:
#         await client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать любое сообщение пользователя, которого вы хотите ограничить")
#         return
#     if reply_msg.from_user.id == msg.from_user.id:
#         await client.send_message(msg.chat.id, "ОГРАНИЧЕНИЕ: Ты не можешь ограничить сам себя.")
#         return
    
#     if is_restricted:
#         is_unrestrict = await unrestrict(client, msg)
#         get_user_data, _ = await get_restricted_data(client, msg)

#         if is_unrestrict:
#             await client.send_message(msg.chat.id, f"С пользователя {get_user_data.first_name} сняты все ограничения")
#         else:
#             await client.send_message(msg.chat.id, f"Пользователь {get_user_data.first_name} не имеет никаких ограничений в этой группе")
