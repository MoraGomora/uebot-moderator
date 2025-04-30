import ujson
import aiofiles

from utils.path_manager import get_storage_path

class JSONManager:

    def __init__(self, filename: str):
        self.filename = filename

    async def read(self) -> dict(): # type: ignore
        async with aiofiles.open(f"{get_storage_path()}/{self.filename}") as file:
            print(file)