from typing import Optional, Any

from pyrogram import Client, filters
from pyrogram.handlers import *

from .log import PluginLog

_handlers = {}
_commands = {}

class PluginCommandRegister(PluginLog):
    """
    A class to register and manage plugin commands.
    """
    def __init__(self):
        super().__init__()
        self.MESSAGE = MessageHandler
        self.EDITED_MESSAGE = EditedMessageHandler
        self.DELETED_MESSAGE = DeletedMessagesHandler
        self.CALLBACK_QUERY = CallbackQueryHandler
        self.INLINE_QUERY = InlineQueryHandler
        self.CHOSEN_INLINE_RESULT = ChosenInlineResultHandler
        self.CHAT_MEMBER = ChatMemberUpdatedHandler
        self.USER_STATUS = UserStatusHandler
        self.POLL = PollHandler
        self.DISCONNECT = DisconnectHandler

    def message_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with MessageHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, message: Any):
            return await handler(client, message)
        
        return self._register_handler(name, handler, self.MESSAGE, command_wrapper, filter, group)

    def edited_message_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with EditedMessageHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, edited_message: Any):
            return await handler(client, edited_message)
        
        return self._register_handler(name, handler, self.EDITED_MESSAGE, command_wrapper, filter, group)
    
    def deleted_message_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with DeletedMessagesHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, deleted_messages: Any):
            return await handler(client, deleted_messages)
        
        return self._register_handler(name, handler, self.DELETED_MESSAGE, command_wrapper, filter, group)

    def callback_query_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with CallbackQueryHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, callback_query: Any):
            return await handler(client, callback_query)
        
        return self._register_handler(name, handler, self.CALLBACK_QUERY, command_wrapper, filter, group)

    def inline_query_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with InlineQueryHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, inline_query: Any):
            return await handler(client, inline_query)
        
        return self._register_handler(name, handler, self.INLINE_QUERY, command_wrapper, filter, group)
    
    def chosen_inline_result_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with ChosenInlineResultHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, chosen_inline_result: Any):
            return await handler(client, chosen_inline_result)
        
        return self._register_handler(name, handler, self.CHOSEN_INLINE_RESULT, command_wrapper, filter, group)
    
    def chat_member_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with ChatMemberUpdatedHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, chat_member_updated: Any):
            return await handler(client, chat_member_updated)
        
        return self._register_handler(name, handler, self.CHAT_MEMBER, command_wrapper, filter, group)
    
    def user_status_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with UserStatusHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, user_status: Any):
            return await handler(client, user_status)
        
        return self._register_handler(name, handler, self.USER_STATUS, command_wrapper, filter, group)
    
    def poll_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with PollHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, poll: Any):
            return await handler(client, poll)
        
        return self._register_handler(name, handler, self.POLL, command_wrapper, filter, group)
    
    def disconnect_handler(self, name: str, handler: callable, filter: Optional[filters.Filter] = None, group: int = 0):
        """
        Register a command with DisconnectHandler.
        :param name: Name of the command
        :param handler: Command function to be executed
        :param filter: Optional filter to apply to the command
        :param group: Group number for the handler
        """
        async def command_wrapper(client: Client, disconnect: Any):
            return await handler(client, disconnect)
        
        return self._register_handler(name, handler, self.DISCONNECT, command_wrapper, filter, group)
    
    # --------------- Private Methods ---------------
    def _register_handler(self, name: str, handler: callable, handler_type: Any, command_wrapper: Any, filter: Optional[filters.Filter] = None, group: int = 0):
        if not callable(handler):
            raise ValueError(f"Command function {handler} is not callable.")
        
        _commands[name] = handler
        command_filter = filter if filter else filters.command(name)

        _handlers[name] = {
            "handler": command_wrapper,
            "filter": command_filter,
            "group": group,
            "handler_type": handler_type
        }

        self.log("debug", f"Command {name} registered with handler: {handler} and filter: {command_filter}")

    def _get_handlers(self) -> dict:
        """
        Get all registered command handlers.
        :return: Dictionary of command handlers
        """
        self.log("debug", "Getting all registered handlers...")
        if not _handlers:
            self.log("warning", "No handlers registered.")
            return {}
        
        return _handlers
