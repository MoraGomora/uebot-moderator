import pathlib
import os

def get_absolute_path():
    return f"{pathlib.Path(__file__).absolute().parent}".split("\\")[:-1][-1]

def get_storage_path():
    return f"{get_absolute_path()}/storage/"