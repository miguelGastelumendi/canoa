"""
 Equipe da Canoa -- 2024

 Some functions that I missed. Brought to Py
 mgd 2024-04-09--27

 """
 # cSpell:ignore latin CCITT

import time
import platform
from datetime import datetime


OS_NAME_IS = platform.system()
OS_IS_WINDOWS = (OS_NAME_IS == "Windows")
OS_IS_LINUX = (OS_NAME_IS == "Linux")
OS_IS_MAC = (OS_NAME_IS == "Darwin")


def now() -> datetime:
    # current date time
    return datetime.now()


def is_str_none_or_empty(s: str) -> bool:
    """
    Returns True if the argument is None of an empty (only spaces, \t, \t, etc) string
    """
    return (s is None) or ((str(s) + '').strip() == '')


def to_str(s: str) -> str:
    """
    Returns the argument as a string, striping spaces
    """
    return '' if is_str_none_or_empty(s) else (s + '').strip()


def strip_and_ignore_empty(s: str, sep = ',', max_split = -1) -> list[str]:
    """
    Returns a list of the striped items created by splitting s and ignoring empty items
    """
    result = []
    for item in (i.strip() for i in to_str(s).split(sep, max_split) if i.strip()):
        if not is_str_none_or_empty(item):
            result.append(item)

    return result


def coalesce(val1, val2):
    """
    Returns the first argument if it's truthy (not empty), otherwise returns the second argument.
    """
    return val1 if val1 else val2


def crc16(data: bytes | str) -> int:
    """
    Calculates CRC16 value for the given data (bytes or string).
    CRC-16/CCITT-FALSE

    https://www.askpython.com/python/examples/crc-16-bit-manual-calculation
    https://crccalc.com/

    data = 'Hello, World!'
    crc16 = crc16(data) -> 0x67DA
    max: 0xFFFF



    Args:
        data: The data to calculate CRC16 for (either bytes or string).

    Returns:
        The calculated CRC16 value (int).
        print(f"{crc16('Hello, World!'):04X}")
    """

    if (data is None):
        return 0
    elif type(data) == bytes:
        pass
    elif not isinstance(data, str):
        raise TypeError('Expecting bytes of str parameter.')
    elif is_str_none_or_empty(data):
        return 0
    else: # Convert string to bytes
        data = data.encode()


    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1

            crc &= 0xFFFF

    return crc


def current_milliseconds():
    """
    max -> d86400000 -> x526 5C00 -> (22)ggi.48g
    """
    return time.time_ns() // 1_000_000


def to_base(number: int, base: int) -> str:
    if base < 2 or base > 36:
        raise ValueError('Base must be between 2 and 36.')

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


def decode_std_text(std_text: bytes):
    """
    Decodes standard output/error from a subprocess, handling potential encoding issues.

    Args:
    output: The byte output from the subprocess.

    Returns:
    A string containing the decoded output.
    """
    if std_text is None or std_text == b'':
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