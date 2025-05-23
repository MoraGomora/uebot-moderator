class PluginCommandRegister:
    """
    A class to register and manage plugin commands.
    """

    def __init__(self):
        self.commands = {}

    def register_command(self, name: str, handler: callable):
        """
        Register a command with its name and function.
        :param command_name: Name of the command
        :param command_func: Function to be executed when the command is called
        """
        if not callable(handler):
            raise ValueError(f"Command function {handler} is not callable.")
        
        self.commands[name] = handler

    def get_handler(self, name: str):
        """
        Get the command function by its name.
        :param command_name: Name of the command
        :return: Command function or None if not found
        """
        return self.commands.get(name, None)
    
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