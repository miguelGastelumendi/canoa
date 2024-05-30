"""
 Equipe da Canoa -- 2024

 Some functions that I missed. Brought to Py
 mgd 2024-04-09--27

 """
 # cSpell:ignore latin

import time
import datetime
from os import path, makedirs


def now():
    # current date time
    return datetime.datetime.now()


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


def folder_must_exist(full_path) -> bool:
    done = path.isdir(full_path)
    try:
        if not done:
            makedirs(full_path)
            done = True
    except Exception as e:
        done = False
        #app.logger.error(f"Error creating folder {full_path}, {e}")

    return done


def is_same_file_name(file1: str, file2: str):
    return path.normcase(file1) == path.normcase(file2)


def is_str_none_or_empty(s: str) -> bool:
   return (s is None) or ((s + '').strip() == '')


def to_str(s: str) -> str:
    return '' if is_str_none_or_empty(s) else (s + '').strip()


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
        base_digits = '0123456789abcdefghijklmnopqrstuvwxyz'[:base]  # Digits for the specified base
        while number:
            number, remainder = divmod(number, base)
            result = base_digits[remainder] + result

    return result

def decode_std_text(std_text):
    """Decodes standard output/error from a subprocess, handling potential encoding issues.

    Args:
    output: The byte output from the subprocess.

    Returns:
    A string containing the decoded output.
    """
    if is_str_none_or_empty(std_text):
        return ''

    try:
        # Try UTF-8 first, as it's commonly used
        return std_text.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 fails, try common encodings for Windows and latin-1
        for encoding in ('latin-1', 'cp1252'):
            try:
                return std_text.decode(encoding)
            except Exception:
                pass

    # If all encodings fail, return the raw bytes as a string
    return str(std_text)

# class MyCustomDict(dict):
#     def __getattr__(self, attr):
#         if attr in self:
#             return self[attr]
#         else:
#             raise AttributeError(f"'MyCustomDict' object has no attribute '{attr}'")

# # Usage:
# my_dict = MyCustomDict({'key1': 'value1', 'key2': 'value2'})


# eof