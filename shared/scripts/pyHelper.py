"""
 Equipe da Canoa -- 2024

 mgd 2024-04-09--27
"""
import time
from os import path


def path_remove_last(dir: str) -> str:
    folders = dir.split(path.sep)
    if len(folders) < 2:
        return None

    short_dir = path.sep.join(folders[:-1])
    return short_dir


def is_str_none_or_empty(s: str) -> bool:
   return True if (s is None) or (s + "").strip() == "" else False

def current_milliseconds():
    # now = datetime.now()
    # midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # return (now - midnight).microseconds // 1000
    return time.time_ns() // 1_000_000

def to_base(number, base):
    if base < 2 or base > 13:
        raise ValueError("Base must be between 2 and 13.")

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
        base_digits = "0123456789ABCDEF"[:base]  # Digits for the specified base
        while number:
            number, remainder = divmod(number, base)
            result = base_digits[remainder] + result

    return result

# eof