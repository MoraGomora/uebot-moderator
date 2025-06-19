import traceback
import inspect
import os
import sys
import asyncio

from utils import path_manager

from .plugin.log import PluginLog
from .plugin.base import PluginBase
from .plugin._metadata import _PluginMetadata
from .plugin._plugin import _Plugin
from .plugin._execution_manager import PluginExecutionManager

_plugins = {}

class PluginLoader(PluginLog):

    def __init__(self):
        super().__init__()

        self._plugin_path = path_manager.get_plugin_path()
        self.plugin_metadata = _PluginMetadata()
        self.plugin = _Plugin()
        self.execution_manager = PluginExecutionManager()

        self._functions = []
        self._missing_functions = []

    def _inspect_functions(self, plugin_name: str, cls, module, data: dict):
        required_methods = ["start", "load"]

        if not self._validate_plugin(plugin_name, module, cls, required_methods):
            self.log("error", f"Plugin '{plugin_name}' is not valid. Skipping function inspection.")
            return

        for name, obj in inspect.getmembers(cls, inspect.isfunction):
            if not name and not obj:
                self.log("error", f"Function {name} in the plugin is empty or not defined!")
                continue

            if obj.__module__ == module.__name__:
                plugin_instance = cls()
                self.log("debug", f"{name = }, {obj = }")

                sig = inspect.signature(obj)
                params = list(sig.parameters.values())
                params = [p for p in params if p.name != "self"]

                if name in required_methods:
                    if not params:
                        self.log("debug", f"Function {name = } in the plugin is a required method")
                        self.execution_manager.add_method(plugin_instance, name)

                        self.log("debug", f"Function {name = } in the plugin doesn't have any arguments")
                        self._call_with_captured_print(data, name)
                    else:
                        self.log("error", f"Function {name = } in the plugin has arguments: {[p.name for p in params]}! This is not allowed!")
                        raise TypeError(f"Function {name = } in the plugin has arguments: {[p.name for p in params]}! This is not allowed!")
        
                self._functions.append({plugin_name: {"name": name, "obj": obj, "params": [p.name for p in params] if params else None}})

    def _validate_plugin(self, plugin_name: str, module, cls, required_methods: list):
        valid = False

        if not isinstance(required_methods, list):
            self.log("error", "Required methods must be a list")
            raise TypeError("required_methods must be a list")
        if not plugin_name or not isinstance(plugin_name, str):
            self.log("error", "Plugin name must be a non-empty string")
            raise TypeError("plugin_name must be a non-empty string")
        if not module or not hasattr(module, "__name__"):
            self.log("error", "Module must be a valid module with a __name__ attribute")
            raise TypeError("module must be a valid module with a __name__ attribute")
        
        has_required_methods = all(
            hasattr(cls, method) and callable(getattr(cls, method))
            for method in required_methods
        )

        if has_required_methods:
            self.log("debug", f"Plugin '{plugin_name}' has all required methods: {required_methods}")
            valid = True
        else:
            self._missing_functions.append({
                "plugin_name": plugin_name,
                "missing_methods": [method for method in required_methods if not hasattr(cls, method) or not callable(getattr(cls, method))]
            })
            self.log("error", f"Plugin '{plugin_name}' is missing required methods: {self._missing_functions}")
        
        for method in required_methods:
            if hasattr(cls, method):
                method_obj = getattr(cls, method)
                if inspect.getsource(method_obj).strip().count('\n') <= 2:
                    self.log("warning", f"Method {method} in plugin {plugin_name} appears to be empty")
                    valid = False
        
        if not valid:
            self.log("error", f"Plugin '{plugin_name}' is not valid. Required methods: {required_methods}")
        
        return valid

    def _inspect_module(self, plugin_name: str, module, data: dict):
        for class_name, cls in inspect.getmembers(module, inspect.isclass):
            if (cls.__module__ == module.__name__ and
                issubclass(cls, PluginBase) and
                cls is not PluginBase):
                self.log("debug", f"{class_name = }, {cls = }")

                self._inspect_functions(plugin_name, cls, module, data)

    def load_plugin(self, plugin_name: str = None, plugin_contains: str = None, files: list = None):
        if plugin_name and plugin_contains and files:
            if not isinstance(plugin_name, str):
                self.log("error", "Plugin name must be a string")
                raise TypeError("plugin_name must be a string")
            if not isinstance(plugin_contains, str):
                self.log("error", "Plugin contains path must be a string")
                raise TypeError("plugin_contains must be a string")
            if not isinstance(files, list):
                self.log("error", "Files must be a list")
                raise TypeError("files must be a list")
        else:
            self.log("error", "Plugin name, contains path and files list must be provided")
            return
        
        self.plugin_metadata._load_plugin_metadata(plugin_name, plugin_contains, files)
        data = self.plugin_metadata.get_metadata(plugin_name)
        module = self.plugin.load_module_from_file(plugin_contains, plugin_name, files, data)

        if module:
            self._inspect_module(plugin_name, module, data)
        
        _plugins[plugin_name] = {
            "data": data,
            "_functions": [func for func in self._functions if plugin_name in func]
        }

        self.log("debug", f"Functions for plugin '{plugin_name}': {data.get('_functions', [])}")

    def load_all_plugins(self):
        if not os.path.exists(self._plugin_path):
            self.log("error", f"Plugin path '{self._plugin_path}' does not exist!")
            return
        
        if not os.path.isdir(self._plugin_path):
            self.log("error", f"Plugin path '{self._plugin_path}' is not a directory!")
            return
        
        for folder_name in os.listdir(self._plugin_path):
            plugin_contains = os.path.join(self._plugin_path, folder_name)

            files = os.listdir(plugin_contains)
            for file in files:
                if os.path.isfile(os.path.join(plugin_contains, file)):
                    if not file.endswith((".py", ".json")) or file in ["__init__.py", "__pycache__"]:
                        continue

            self.load_plugin(folder_name, plugin_contains, files)
                
    # def unload_plugin(self, plugin_name: str):
    #     if plugin_name in _plugins:
    #         plugin = _plugins[plugin_name]
    #         unload = getattr(plugin, "unload", None)

    #         if callable(unload):
    #             unload()

    #         del loaded_plugins[plugin_name]
    #         del sys.modules[plugin_name]
    #         print(f"[-] Плагин '{plugin_name}' выгружен")
    #     else:
    #         print(f"[X] Плагин {plugin_name} не был загружен")

    # def reload_plugin(self, plugin_name: str):
    #     self.unload_plugin(plugin_name)
    #     return self.load_plugin()

    def run_all_plugins(self):
        for name, data in _plugins.items():
            plugin_data = data.get("data", {})
            module = plugin_data.get("module", None)

            if not module:
                self.log("error", f"Module for plugin {name} is not found!")
                continue

            self.log("debug", f"Running plugin: {name}")

            try:
                run = getattr(module, "start", None)

                if not run:
                    self.log("error", f"Plugin {name} does not have a 'start' method!")
                    continue
                
                if callable(run):
                    skipped_count = self.get_missing_functions_count()
                    print(skipped_count)
                    if inspect.iscoroutinefunction(run):
                        self.log("debug", f"Plugin {name} has a coroutine 'start' method, running it asynchronously")
                        self.log("debug", f"Skipped plugins: {skipped_count}")
                        asyncio.run(run())
                    else:
                        self.log("debug", f"Plugin {name} has a regular 'start' method, running it synchronously")
                        run()
                self.execution_manager.execute_all()
            except Exception as e:
                self.log("error", f"Error while running plugin {name}: {e}")

    def load_and_run_all_plugins(self):
        self.load_all_plugins()
        self.run_all_plugins()

    def get_all_plugins(self):
        return _plugins
    
    def get_plugin(self, plugin_name: str):
        return _plugins.get(plugin_name, None)
    
    def get_missing_functions(self):
        return self._missing_functions
    
    def get_missing_functions_count(self):
        return len(self._missing_functions)
    





"""
Сейчас надо сделать так, чтобы при загрузке плагинов, если в них есть методы, которые не соответствуют требованиям, то они не вызывались и не регистрировались.
"""






"""
# plugin_engine.py

import importlib.util
import logging
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Callable, List

logger = logging.getLogger("PluginEngine")

class PluginContext:
def **init**(self, user: str, bot\_api: Any, db: Any, is\_premium: bool = False):
self.user = user
self.bot = bot\_api
self.db = db
self.is\_premium = is\_premium
self.logger = logging.getLogger("PluginContext")
self.\_event\_hooks: Dict\[str, List\[Callable]] = {}

```
def get(self, key: str):
    return getattr(self, key, None)

def register_event_hook(self, event_type: str, handler: Callable):
    if event_type not in self._event_hooks:
        self._event_hooks[event_type] = []
    self._event_hooks[event_type].append(handler)
    self.logger.debug(f"Registered hook for {event_type}: {handler}")

def get_event_hooks(self, event_type: str) -> List[Callable]:
    return self._event_hooks.get(event_type, [])
```

class Plugin:
def **init**(self, path: Path):
self.path = path
self.manifest = self.\_load\_manifest()
self.module = None
self.enabled = True  # Default enabled
self.handlers\_registered = False

```
def _load_manifest(self) -> Dict[str, Any]:
    manifest_file = self.path / "manifest.yaml"
    if not manifest_file.exists():
        raise FileNotFoundError(f"No manifest found in {self.path}")
    return yaml.safe_load(manifest_file.read_text())

def load(self):
    main_file = self.path / "main.py"
    if not main_file.exists():
        raise FileNotFoundError(f"No main.py in {self.path}")

    spec = importlib.util.spec_from_file_location(self.manifest["name"], main_file)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        self.module = module
    except Exception as e:
        logger.error(f"Error loading plugin {self.manifest['name']}: {e}")
        self.module = None

def execute(self, event: Dict[str, Any], context: PluginContext):
    if self.enabled and self.module and hasattr(self.module, "handle"):
        try:
            self.module.handle(event, context)
        except Exception as e:
            logger.error(f"Error executing plugin {self.manifest['name']}: {e}")

def register_handlers(self, app):
    if self.module and hasattr(self.module, "register_handlers"):
        try:
            self.module.register_handlers(app)
            self.handlers_registered = True
            logger.info(f"Handlers registered from plugin: {self.manifest['name']}")
        except Exception as e:
            logger.error(f"Error registering handlers from plugin {self.manifest['name']}: {e}")
    else:
        logger.warning(f"⚠️ Handlers from {self.manifest['name']} not registered (missing register_handlers)")
```

class PluginEngine:
def **init**(self, plugin\_folder: str, user: str, bot\_api: Any, db: Any, is\_premium: bool = False):
self.plugin\_folder = Path(plugin\_folder)
self.plugins: Dict\[str, Plugin] = {}
self.context = PluginContext(user, bot\_api, db, is\_premium)
self.ready = False

```
def load_plugins(self):
    if not self.plugin_folder.exists():
        logger.warning("Plugin folder does not exist.")
        return

    for item in self.plugin_folder.iterdir():
        if item.is_dir():
            try:
                plugin = Plugin(item)
                plugin.load()
                if plugin.module:
                    self.plugins[plugin.manifest["name"]] = plugin
                    if hasattr(plugin.module, "register"):
                        try:
                            plugin.module.register(self.context)
                        except Exception as e:
                            logger.warning(f"Plugin {plugin.manifest['name']} failed to register hooks: {e}")
                    logger.info(f"Loaded plugin: {plugin.manifest['name']}")
                else:
                    logger.warning(f"⚠️ Plugin {plugin.manifest['name']} was not fully loaded (no module)")
            except Exception as e:
                logger.error(f"Failed to load plugin in {item.name}: {e}")

def register_all_handlers(self, app):
    handler_count = 0
    for plugin in self.plugins.values():
        if plugin.enabled:
            plugin.register_handlers(app)
            if plugin.handlers_registered:
                handler_count += 1
    logger.info(f"✅ Total plugins with handlers registered: {handler_count} / {len(self.plugins)}")
    self.ready = True
    logger.info("🚀 PluginEngine is ready.")

def trigger_event(self, event: Dict[str, Any]):
    event_type = event.get("type")
    # Run registered hooks first
    for handler in self.context.get_event_hooks(event_type):
        try:
            handler(event)
        except Exception as e:
            logger.error(f"Error in event hook for {event_type}: {e}")

    # Then let plugins handle normally if needed
    for plugin in self.plugins.values():
        if not plugin.enabled:
            continue
        if event_type in plugin.manifest.get("events", []):
            requires_premium = plugin.manifest.get("requires_premium", False)
            if requires_premium and not self.context.is_premium:
                logger.info(f"Skipping plugin {plugin.manifest['name']} (premium-only)")
                continue
            plugin.execute(event, self.context)

def list_plugins(self) -> Dict[str, Dict[str, Any]]:
    return {name: p.manifest for name, p in self.plugins.items()}

def enable_plugin(self, name: str) -> bool:
    plugin = self.plugins.get(name)
    if plugin:
        plugin.enabled = True
        return True
    return False

def disable_plugin(self, name: str) -> bool:
    plugin = self.plugins.get(name)
    if plugin:
        plugin.enabled = False
        return True
    return False

def plugin_status(self) -> Dict[str, bool]:
    return {name: plugin.enabled for name, plugin in self.plugins.items()}
```
"""