import os
import aiofiles

import ujson

from .path_manager import get_storage_path

class JSONManager:

    def __init__(self, filename: str):
        self._filename = filename
        self._file_format = ".json"
        self.filepath = f"{get_storage_path()}/{self._filename + self._file_format}"
        self._raw_data = None
        self._error = None

    async def read(self) -> dict | None: # type: ignore
        if not os.path.exists(self.filepath):
            self._error = f"File {self.filepath} is not available"

        try:
            async with aiofiles.open(self.filepath, "r", encoding="utf-8") as file:
                self._raw_data = await file.read()

                if self._raw_data == "":
                    return None

                return ujson.loads(self._raw_data)
        except ujson.JSONDecodeError as e:
            self._error = f"Something was happened in 'read()': {e}"
        
    async def write(self, data: dict):
        if self._raw_data is None:
            await self.read()

        try:
            async with aiofiles.open(self.filepath, "w", encoding="utf-8") as f:
                if self.is_curly_brackets_available():
                    json = dict(ujson.loads(self._raw_data))

                    json.update(data)

                    new_json = ujson.dumps(json, ensure_ascii=False, indent=4)
                    await f.write(new_json)
                else:
                    json = ujson.dumps(data, ensure_ascii=False, indent=4)
                    await f.write(json)
        except ujson.JSONDecodeError as e:
            self._error = f"Something was happened in 'write()': {e}"
            
    def is_curly_brackets_available(self) -> bool:
        return False if not (self._raw_data.startswith("{") and self._raw_data.endswith("}")) else True
    
    def get_filename(self) -> str:
        return self._filename + self._file_format

    def has_error(self) -> str | None:
        return self._error is not None
    
    def get_error(self) -> str:
        return self._error
