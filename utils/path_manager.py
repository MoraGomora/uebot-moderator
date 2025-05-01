import pathlib
import os

def _get_absolute_path():
    path = f"{pathlib.Path(__file__).absolute().parent}".split("\\")[:-1]
    return "/".join(path)

def get_storage_path():
    return f"{_get_absolute_path()}/storage"

def get_session_path():
    path = f"{_get_absolute_path()}/storage/sessions"

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def is_file_in_storage_available(filename: str) -> bool:
    return False if not os.path.exists(f"{get_storage_path()}/{filename}") else True