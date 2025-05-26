import inspect
import asyncio
from .log import PluginLog

class PluginExecutionManager(PluginLog):
    def __init__(self):
        super().__init__()
        self.log("debug", "PluginExecutionManager initialized")
        self.scheduled_methods = []
        
    def add_method(self, instance, method_name):
        if callable(getattr(instance, method_name, None)):
            self.log("debug", f"Adding method {method_name} from {instance.__class__.__name__}")
            self.scheduled_methods.append((instance, method_name))
        
    def execute_all(self):
        for instance, method_name in self.scheduled_methods:
            self.log("debug", f"Executing method {method_name} from {instance.__class__.__name__}")
            if not hasattr(instance, method_name):
                self.log("error", f"Method {method_name} not found in {instance.__class__.__name__}")
                continue
            try:
                method = getattr(instance, method_name)
                if not callable(method):
                    self.log("error", f"{method_name} is not callable in {instance.__class__.__name__}")
                    continue
                if inspect.iscoroutinefunction(method):
                    asyncio.create_task(method())
                else:
                    method()
            except Exception as e:
                self.log("error", f"Error executing {method_name} in {instance.__class__.__name__}: {e}")