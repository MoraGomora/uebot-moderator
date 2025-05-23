import importlib.util
import inspect
import sys
import asyncio

from .log import PluginLog

class _Plugin(PluginLog):

    def __init__(self):
        super().__init__()
        self._main_base_filename = "main.py"

    def load_module_from_file(self, file_path: str, folder_name: str, files: list, metadata: dict) -> object | None:
        """
        Load a module from a file path
        :param file_path: Path to the plugin folder
        :param folder_name: Name of the plugin folder
        :param files: List of files in the plugin folder
        :return: Loaded module or None
        """

        if not metadata:
            self.log("error", f"❌ Plugin {folder_name} is not loaded. The plugin will not be loaded")
            return None

        if self._main_base_filename in files:
            spec = importlib.util.spec_from_file_location(metadata["name"], f"{file_path}/{self._main_base_filename}")
        
            if spec and spec.loader:
                try:
                    module = importlib.util.module_from_spec(spec)
                    metadata["module"] = module
                    sys.modules[folder_name] = module
                    spec.loader.exec_module(module)

                    self.log("debug", f"The module from {metadata["name"]} is loaded successfully")
                    return module
                except Exception as e:
                    self.log("error", f"Something was happened: {e}")
                    return None
            else:
                self.log("error", f"❌ Failed to create a specification! 'spec' value: {spec}")
        else:
            self.log("error", f"❌ main.py file was not found in plugin {metadata["name"]} (version: {metadata["version"]}). " \
                "The plugin will not be loaded")

    def entry_load(self, plugin_name, entry_function: str):
        entry_func = getattr(plugin_name, entry_function, None)

        if callable(entry_func):
            if inspect.iscoroutinefunction(entry_func):
                asyncio.create_task(entry_func())
            else:
                entry_func()