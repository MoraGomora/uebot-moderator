import pathlib

def _get_absolute_path():
    path = f"{pathlib.Path(__file__).absolute().parent}".split("\\")[:-1]
    return "/".join(path)

def get_storage_path():
    return f"{_get_absolute_path()}/storage"