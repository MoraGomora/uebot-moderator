import logging
import datetime
import os

class Log():
    def __init__(self, name: str | None = "userbot-moderator", level = logging.DEBUG):
        self._log_dir = "logs"
        self._log_name = f"app_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self._level = level

        self._logger = logging.getLogger(name)

        if not self._logger.handlers:
            self.console_handler = logging.StreamHandler()
            self._formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            self.console_handler.setFormatter(self._formatter)
            self.console_handler.setLevel(self._level)
            self._logger.addHandler(self.console_handler)

    def write_logs_to_file(self):
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir, exist_ok=True)

        file_handler = logging.FileHandler(f"{self._log_dir}/{self._log_name}", encoding="utf-8")
        file_handler.setFormatter(self._formatter)
        file_handler.setLevel(self._level)

        self._logger.addHandler(file_handler)

    def getLogger(self):
        return self._logger