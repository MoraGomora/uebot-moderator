import inspect
import sys
import io

from typing import Literal

from logger import Log

_log = Log("loader")
_log.getLogger().setLevel("DEBUG")
_log.write_logs_to_file()

class _PluginStdout(io.StringIO):

    def __init__(self, plugin_name, loader):
        super().__init__()
        self._loader = loader
        self.plugin_name = plugin_name

    def write(self, s):
        s = s.strip()
        if s:
            self._loader("debug", f"The plugin {self.plugin_name} print: {s}")


class PluginLog:
    def __init__(self):
        self._log = _log

    def log(self, level: Literal["debug", "info", "warning", "error", "critical"], msg: str):

        if not isinstance(msg, str):
            raise TypeError("msg must be a string")
        
        def get_caller_fullname():
            frame = inspect.currentframe()

            for i in range(2):
                if frame:
                    frame = frame.f_back
            
            if not frame:
                return "<unknown>"
            
            code = frame.f_code
            func_name = code.co_name
            module = inspect.getmodule(code)
            module_name = module.__name__ if module else "<unknown_module>"

            cls_name = None
            self_obj = frame.f_locals.get("self")
            if self_obj:
                cls_name = type(self_obj).__name__

            if cls_name:
                return f"{module_name}.{cls_name}.{func_name}"
            else:
                return f"{module_name}.{func_name}"
            
        caller_name = get_caller_fullname()

        if level == "debug":
            self._log.getLogger().debug(f"[LOADER][DEBUG] - [{caller_name}]: {msg}")
        elif level == "info":
            self._log.getLogger().info(f"[LOADER][INFO] - [{caller_name}]: {msg}")
        elif level == "warning":
            self._log.getLogger().warning(f"[LOADER][WARNING] - [{caller_name}]: {msg}")
        elif level == "error":
            self._log.getLogger().error(f"[LOADER][ERROR] - [{caller_name}]: {msg}")
        elif level == "critical":
            self._log.getLogger().critical(f"[LOADER][CRITICAL] - [{caller_name}]: {msg}")
        else:
            raise ValueError("[LOADER] Invalid log level. Choose from: debug, info, warning, error, critical")

    def _call_with_captured_print(self, plugin_data: dict, method_name, *args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = _PluginStdout(plugin_data.get("name"), self.log)
        try:
            result = getattr(plugin_data.get("module"), method_name)(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
        return result

    def _call_and_capture_return(self, plugin_data: dict, method_name: str, *args, **kwargs):
        result = getattr(plugin_data.get("module"), method_name)(*args, **kwargs)
        self.log("debug", f"The plugin {plugin_data.get("name")} return: {result}")
        return result