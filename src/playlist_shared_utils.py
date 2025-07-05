import os
from src.setup_logging import raise_and_log


def check_file_type(file_name: str, file_exts: list[str]) -> bool:
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in file_exts:
        if len(file_exts) == 1:
            raise_and_log(ValueError, f"Invalid file type: {ext}. Allowed type is {file_exts}")
        else:
            raise_and_log(ValueError, f"Invalid file type: {ext}. Allowed types are {file_exts}")
    return True
