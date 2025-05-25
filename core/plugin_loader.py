import traceback
import inspect
import os
import sys

from utils import path_manager

from .plugin.log import PluginLog
from .plugin.base import PluginBase
from .plugin._metadata import _PluginMetadata
from .plugin._plugin import _Plugin
from .plugin._execution_manager import PluginExecutionManager

loaded_plugins = {}
_plugins = {}


class PluginLoader(PluginLog):

    def __init__(self):
        super().__init__()

        self._plugin_path = path_manager.get_plugin_path()
        self.plugin_metadata = _PluginMetadata()
        self.plugin = _Plugin()
        self.execution_manager = PluginExecutionManager()

        self._functions = []

    def inspect_module(self, folder_name: str, module, data: dict):
        required_methods = ["start", "load"]

        for class_name, cls in inspect.getmembers(module, inspect.isclass):
            if (cls.__module__ == module.__name__ and
                issubclass(cls, PluginBase) and
                cls is not PluginBase):
                self.log("debug", f"{class_name = }, {cls = }")

                for name, obj in inspect.getmembers(cls, inspect.isfunction):
                    if obj.__module__ == module.__name__:
                        plugin_instance = cls()
                        # print(f"{name = }, {obj = }")
                        self.log("debug", f"{name = }, {obj = }")

                        sig = inspect.signature(obj)
                        params = list(sig.parameters.values())
                        params = [p for p in params if p.name != "self"]

                        if name in required_methods:
                            if not params:
                                self.log("debug", f"Function {name = } in the plugin is a required method")
                                # self.plugin.entry_load(obj(), name)
                                self.execution_manager.add_method(plugin_instance, name)

                                self.log("debug", f"Function {name = } in the plugin doesn't have any arguments")
                                self._call_with_captured_print(data, name)
                            else:
                                self.log("error", f"Function {name = } in the plugin has arguments: {[p.name for p in params]}! This is not allowed!")
                                raise TypeError(f"Function {name = } in the plugin has arguments: {[p.name for p in params]}! This is not allowed!")
                
                self._functions.append({folder_name: {"name": name, "obj": obj, "params": [p.name for p in params] if params else None}})

    async def load_plugin(self):
        for folder_name in os.listdir(self._plugin_path):
            plugin_contains = os.path.join(self._plugin_path, folder_name)

            files = os.listdir(plugin_contains)
            for file in files:
                if os.path.isfile(os.path.join(plugin_contains, file)):
                    if not file.endswith((".py", ".json")) or file in ["__init__.py", "__pycache__"]:
                        continue

            self.plugin_metadata._load_plugin_metadata(folder_name, plugin_contains, files)
            data = self.plugin_metadata.get_metadata(folder_name)
            module = self.plugin.load_module_from_file(plugin_contains, folder_name, files, data)

            if module:
                self.inspect_module(folder_name, module, data)
            
            _plugins: dict = {
                folder_name: data,
                "functions": [func for func in self._functions if folder_name in func]
            }

        self.execution_manager.execute_all()

            # _plugins[folder_name] = data
            # _plugins[folder_name]["functions"] = self._functions


                
    def unload_plugin(self, plugin_name: str):
        if plugin_name in loaded_plugins:
            plugin = loaded_plugins[plugin_name]
            unload = getattr(plugin, "unload", None)

            if callable(unload):
                unload()

            del loaded_plugins[plugin_name]
            del sys.modules[plugin_name]
            print(f"[-] Плагин '{plugin_name}' выгружен")
        else:
            print(f"[X] Плагин {plugin_name} не был загружен")

    def reload_plugin(self, plugin_name: str):
        self.unload_plugin(plugin_name)
        return self.load_plugin()

    def run_all_plugins(self):
        for name, module in loaded_plugins.items():
            try:
                run = getattr(module, "run")
                
                if callable(run):
                    print(f"▶️ Запуск плагина: {name}")
                    run()
            except Exception as e:
                print(e)

    def get_all_plugins(self):
        return _plugins
    
    def get_plugin(self, plugin_name: str):
        return _plugins.get(plugin_name, None)
    





"""Нам нужно в список загруженных плагинов добавлять собранные данные о плагинах, будь-то их метаданные, корневые модули и т.д.
Надо делать не так, как сейчас, а собирать сначала все данные, вносить их в словарь, а потом к основному словарю добавлять собранные
данные по названию модуля из метаданных или названию папки"""






"""
import sys
import io
import inspect

class PluginStdout(io.StringIO):
    def __init__(self, plugin_name, loader_print):
        super().__init__()
        self.plugin_name = plugin_name
        self.loader_print = loader_print

    def write(self, s):
        s = s.strip()  # убираем лишние переносы строк
        if s:
            self.loader_print(f"Плагин {self.plugin_name} вывел через print: {s}")

def loader_print(msg):
    print(f"[Загрузчик] {msg}")

def call_with_captured_print(plugin, method_name, *args, **kwargs):
    old_stdout = sys.stdout
    sys.stdout = PluginStdout(plugin.__class__.__name__, loader_print)
    try:
        result = getattr(plugin, method_name)(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    loader_print(f"Плагин {plugin.__class__.__name__} вернул: {result}")
    return result

def analyze_and_call(plugin, method_name):
    method = getattr(plugin, method_name)
    sig = inspect.signature(method)
    params = list(sig.parameters.values())
    params = [p for p in params if p.name != "self"]
    if not params:
        loader_print(f"Метод {method_name} не требует аргументов")
        return call_with_captured_print(plugin, method_name)
    else:
        loader_print(f"Метод {method_name} требует аргументов: {[p.name for p in params]}")
        # Пример: передаём значения (можно реализовать свою логику)
        args = [42 for _ in params]
        return call_with_captured_print(plugin, method_name, *args)

# Пример использования
class ExamplePlugin:
    def on_load(self):
        print("Плагин загружен")
        return "ok"
    def on_event(self, value):
        print(f"Событие с аргументом {value}")
        return value * 2

plugin = ExamplePlugin()
analyze_and_call(plugin, "on_load")
analyze_and_call(plugin, "on_event")
"""