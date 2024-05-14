"""
 Equipe da Canoa -- 2024

 mgd 2024-04-09--27
"""
import time
import datetime
from os import path

# { now ===================================================
def now():
    """
        current date time
    """
    return datetime.datetime.now()
# now } ---------------------------------------------------


# { now_for_user ==========================================
def now_for_user():
    """
        current date time for user
        -- TODO: get from ui_texts
    """
    return now().strftime('%d/%m/%Y às %H:%M')
# now_for_user } ------------------------------------------

def path_remove_last(dir: str) -> str:
    folders = dir.split(path.sep)
    if len(folders) < 2:
        return None

    short_dir = path.sep.join(folders[:-1])
    return short_dir


def change_file_ext(file: str, ext: str):
    root, _ = path.splitext(file)
    new_file= root + ext
    return new_file

def is_same_file_name(file1: str, file2: str):
    return path.normcase(file1) == path.normcase(file2)

def is_str_none_or_empty(s: str) -> bool:
   return True if (s is None) or (s + "").strip() == "" else False

def current_milliseconds():
    """
        max -> d86400000 -> x526 5C00 -> (22)ggi.48g
    """
    return time.time_ns() // 1_000_000

def to_base(number, base):
    if base < 2 or base > 36:
        raise ValueError("Base must be between 2 and 36.")

    result = ''
    if number == 0:
        result = '0'
    elif base == 2:
        result = format(number, 'b')
    elif base == 8:
        result = format(number, 'o')
    elif base == 16:
        result = format(number, 'x')
    else:
        base_digits = "0123456789abcdefghijklmnopqrstuvwxyz"[:base]  # Digits for the specified base
        while number:
            number, remainder = divmod(number, base)
            result = base_digits[remainder] + result

    return result

# eof