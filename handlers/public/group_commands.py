import asyncio

from pyrogram.enums import ChatMemberStatus

from core.ai_manager import AIManager
from ._actions import ModerationActions
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("GroupCommands")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

class GroupCommands:
    def __init__(self, client):
        """Initialize the GroupCommands class with a client instance.
        :param client: The client instance to interact with the Telegram API.
        """
        self.client = client

        self.ai = AIManager()
        self.mod_actions = ModerationActions(self.client)

    async def get_restricted_data(self, _, msg):
        try:
            reply_msg = getattr(msg, "reply_to_message", None)
            if reply_msg is None:
                await self.client.send_message(msg.chat.id, "Чтобы команда сработала, вам нужно ответить на любое сообщение интересующего вас пользователя.")
                return None
            if getattr(reply_msg, "sender_chat", None):
                await self.client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать сообщение пользователя, а не группы или канала.")
                return None

            user = await self.client.get_chat_member(msg.chat.id, reply_msg.from_user.id)
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
            await self.client.send_message(msg.chat.id, f"Something was happened: {e}")

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

    async def restrict_process(self, _, msg):
        """Process the restriction command in a group chat.
        :param _: Unused parameter, kept for compatibility with the handler signature.
        :param msg: The message object containing the command and context.
        """

        processing_messages = set()
        msgs = {}

        try:
            reply_msg = getattr(msg, "reply_to_message", None)
            msg_id = f"{msg.chat.id}_{msg.from_user.id}_{msg.id}"

            if msg_id in processing_messages:
                await self.client.send_message(msg.chat.id, "Команда уже выполняется. Пожалуйста, подождите.")
                return
            if reply_msg is None:
                await self.client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать любое сообщение пользователя, которого вы хотите ограничить")
                return
            # if reply_msg.from_user.id == msg.from_user.id:
            #     await self.client.send_message(msg.chat.id, "ОГРАНИЧЕНИЕ: Ты не можешь ограничить сам себя.")
            #     return

            async for message in self.client.get_chat_history(msg.chat.id, limit=15):
                msgs += msgs.update({message.from_user.first_name: message.text})
            print(msgs)
            await self.ai.analyze_message_context(msgs)
                # print(f"{message.text = }{message.from_user.first_name = }")
            
            processing_messages.add(msg_id)

            print(f"Processing restriction for message ID: {msg_id} in chat ID: {msg.chat.id}")

            def handle_ai_decision(task):
                try:
                    decision = task.result()
                    # Создаем новую task для применения решения
                    asyncio.create_task(self._handle_decision(
                        decision, 
                        reply_msg,
                        msg,
                        self.mod_actions
                    ))
                except Exception as e:
                    _log.getLogger().error(f"Error in AI decision handler: {e}")
                finally:
                    processing_messages.remove(msg_id)

            decision_task = asyncio.create_task(self.ai.analyze_message(msg.text))
            decision_task.add_done_callback(handle_ai_decision)

        except Exception as e:
            _log.getLogger().error(f"Something went wrong while processing restriction: {e}")
            await self.client.send_message(msg.chat.id, f"Something was happened: {e}")
            if msg_id in processing_messages:
                processing_messages.remove(msg_id)

    async def _handle_decision(self, decision, reply_msg, msg, mod_actions):
        """Handle the AI decision and apply the appropriate moderation action.
        :param decision: The decision object returned by the AI manager.
        :param reply_msg: The message object to which the command was replied.
        :param msg: The original message object containing the command.
        :param mod_actions: The ModerationActions instance to apply the decision.
        """
        try:
            if not decision:
                _log.getLogger().debug("No decision made by AI.")
                return

            user_id = reply_msg.from_user.id
            chat_id = msg.chat.id

            _log.getLogger().debug(f"Applying moderation decision for user {user_id} in chat {chat_id}: {decision}")

            if decision.confidence < 0.5:
                await self.client.send_message(chat_id, f"AI не уверен в своем решении для пользователя {user_id}. Пожалуйста, проверьте вручную.")
            else:
                member = await self.client.get_chat_member(chat_id, user_id)

                if member is None:
                    _log.getLogger().error(f"User {user_id} is not a member of chat {chat_id}")
                    await self.client.send_message(chat_id, "Пользователь не найден в чате.")
                    return False

                if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    _log.getLogger().debug(f"User {user_id} is an admin or owner in chat {chat_id}, cannot ban.")
                    await self.client.send_message(chat_id, f"Не удалось применить решение {decision.action.name}, так как пользователь является администратором или владельцем чата.")
                    return False
            
                await mod_actions.apply_decision(
                    reply_msg.chat.id,
                    reply_msg.from_user.id,
                    decision
                )
        
        except Exception as e:
            _log.getLogger().error(f"Error applying moderation decision: {e}")
            await self.client.send_message(msg.chat.id, f"Something was happened: {e}")

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
