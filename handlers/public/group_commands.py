import asyncio

from pyrogram.enums import ChatMemberStatus

from core.ai_manager import AIManager
from ._actions import ModerationActions
from logger import Log
from constants import STANDARD_LOG_LEVEL

from .group.message import MessageContext, MessageActions
from .group.restrict import RestrictActions

from ._behavior_manager import BehaviorManager
from ._ad_detector import AdDetector

from utils.messages import format_user_restriction_info

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
        self.mod_actions = ModerationActions(client)
        self.restrict = RestrictActions(client)
        self.message = MessageActions(client)

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

    async def restrict_process(self, _, msg):
        reply_msg = getattr(msg, "reply_to_message", None)
        is_restricted = await self.restrict.is_user_restricted(_, msg)

        if reply_msg is None:
            await self.client.send_message(msg.chat.id, "Чтобы команда сработала, необходимо выбрать любое сообщение пользователя, которого вы хотите ограничить")
            return
        if reply_msg.from_user.id == msg.from_user.id:
            await self.client.send_message(msg.chat.id, "ОГРАНИЧЕНИЕ: Ты не можешь ограничить сам себя.")
            return
        
        if not is_restricted:
            is_restrict = await self.restrict.restrict(msg.chat.id, reply_msg.from_user.id, None)
            get_user_data, get_restricted_by = await self.get_restricted_data(_, msg)
            message = format_user_restriction_info(get_user_data, msg.from_user, get_restricted_by, None)

            if is_restrict:
                # await self.message.delete_message(msg.chat.id, reply_msg.from_user.id)
                await self.client.send_message(msg.chat.id, message)
            else:
                await self.client.send_message(msg.chat.id, f"Пользователь {get_user_data.first_name} уже ограничен")

    async def autorestrict_process(self, _, msg):
        """
        Process the restriction command in a group chat.
        :param _: Unused parameter, kept for compatibility with the handler signature.
        :param msg: The message object containing the command and context.
        """
        behavior_manager = BehaviorManager()
        ad_detector = AdDetector()
        processing_messages = set()

        analyze_method, is_triggered = await behavior_manager.check_offensive_behavior(msg.text)
        reason, method, is_ad = ad_detector.detect_ad_message(msg)

        _triggered_by = getattr(msg, "from_user", getattr(msg, "sender_chat", None))
        if _triggered_by is None:
            _log.getLogger().error("Message does not have a valid user or sender_chat.")
            await self.client.send_message(msg.chat.id, "Ошибка: сообщение не содержит информации о пользователе или отправителе.")
            return
        
        try:
            msg_id = f"{msg.chat.id}_{msg.from_user.id}_{msg.id}"

            if is_ad:
                await self._moderate(msg, msg_id, processing_messages, method)
                _log.getLogger().debug(f"Ad Detected: {is_ad = }, {msg.id = }, {msg_id = }, {reason = }, {method = }")
            
            if is_triggered:
                await self._moderate(msg, msg_id, processing_messages, analyze_method)
                _log.getLogger().debug(f"Behavior patterns triggered: {is_triggered = }, {msg.id = }, {msg_id = }, {analyze_method = }")
        except Exception as e:
            _log.getLogger().error(f"Something went wrong while processing restriction: {e}")
            await self.client.send_message(msg.chat.id, f"Something was happened: {e}")
            if msg_id in processing_messages:
                processing_messages.remove(msg_id)

    async def _moderate(self, msg, msg_id: str, processing_messages: set, analyze_method: str):
        if msg_id in processing_messages:
            await self.client.send_message(msg.chat.id, "Сообщение уже обрабатывается. Пожалуйста, подождите.")
            return

        context = await self.build_context(msg)
        processing_messages.add(msg_id)

        print(f"Processing restriction for message ID: {msg_id} in chat ID: {msg.chat.id}")

        def handle_ai_decision(task):
            try:
                decision = task.result()
                asyncio.create_task(self._handle_decision(
                    decision,
                    msg,
                    self.mod_actions
                ))
            except Exception as e:
                _log.getLogger().error(f"Error in AI decision handler: {e}")
            finally:
                processing_messages.remove(msg_id)

        decision_task = asyncio.create_task(self.ai.analyze_message_context(context, analyze_method))
        decision_task.add_done_callback(handle_ai_decision)

    async def _handle_decision(self, decision, msg, mod_actions):
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

            user_id = msg.from_user.id
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
                    chat_id,
                    user_id,
                    decision
                )
        
        except Exception as e:
            _log.getLogger().error(f"Error applying moderation decision: {e}")
            await self.client.send_message(msg.chat.id, f"Something was happened: {e}")

    async def build_context(self, msg):
        """Build a message context from a list of messages.
        :param msgs: List of MessageContext.Message objects.
        :return: List of dictionaries representing the message context.
        """
        context = MessageContext()
        _triggered_by = getattr(msg, "from_user", getattr(msg, "sender_name", None))
        msgs = []

        async for message in self.client.get_chat_history(msg.chat.id, limit=20):
            msgs.append(MessageContext.Message(
                sender_name=message.from_user.first_name,
                text=message.text or "",
                datetime=message.date.strftime("%Y-%m-%d %H:%M:%S"),
                triggered_by=_triggered_by.first_name if _triggered_by else "Unknown",
                reply_to=message.reply_to_message.text if message.reply_to_message else None
            ))

        context_list = context.build_message_context(msgs)
        return context_list

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
