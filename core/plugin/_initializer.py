from pyrogram import Client

from .log import PluginLog
from .register import PluginCommandRegister

class _PluginCommandInializer(PluginLog):
    """
    A class to initialize plugin commands.
    """

    def __init__(self):
        super().__init__()
        self._handlers = PluginCommandRegister()._get_handlers()

    def _register_handlers(self, client: Client):
        """
        Register all handlers with the client.
        :param client: Pyrogram client instance
        """
        if self._handlers:
            self.log("debug", "Registering handlers...")
            for name, data in self._handlers.items():
                # Check if the handler type is valid
                if data["handler_type"]:
                    self._handler_type(client, name, data, data["handler_type"])
                else:
                    self.log("error", f"Handler type for command {name} is not specified or invalid.")
        else:
            self.log("warning", "No handlers to register.")
            return
        # Log the completion of handlers registration
        self.log("debug", "Handlers registration completed.")

    def _handler_type(self, client, name, data, handler_type):
        """
        Register the handler type with the client.
        :param client: Pyrogram client instance
        :param name: Name of the command
        :param data: Data associated with the command
        :param handler_type: Type of the handler (MessageHandler, CallbackQueryHandler, etc.)
        """
        if data["handler_type"] == handler_type:
            client.add_handler(
                handler_type(
                    data["handler"], data["filter"]),
                    group=data["group"]
            )
            self.log("debug", f"{handler_type} for command {name} registered with filter: {data['filter']} and group: {data['group']}")

    # def get_handler(self, name: str):
    #     """
    #     Get the command function by its name.
    #     :param command_name: Name of the command
    #     :return: Command function or None if not found
    #     """
    #     self.log("debug", f"Getting handler for command: {name}")

    #     if name not in _commands:
    #         self.log("warning", f"Command {name} not found.")
    #         return None
        
    #     return _commands.get(name, None)
    
    # def get_handlers(self):
    #     """
    #     Get all registered command handlers.
    #     :return: Dictionary of command handlers
    #     """
    #     self.log("debug", "Getting all registered handlers...")
    #     if not _handlers:
    #         self.log("warning", "No handlers registered.")
    #         return None
        
    #     self.log("debug", f"Registered handlers: {_handlers}")
    #     return _handlers
    
    def execute_command(self, name: str, *args, **kwargs):
        """
        Execute the command by its name with optional arguments.
        :param command_name: Name of the command
        :param args: Positional arguments for the command function
        :param kwargs: Keyword arguments for the command function
        :return: Result of the command function or None if not found
        """
        command_func = self.get_handler(name)
        
        if command_func:
            return command_func(*args, **kwargs)
        else:
            raise ValueError(f"Command {name} not found.")