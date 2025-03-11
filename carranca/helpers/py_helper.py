"""
 Equipe da Canoa -- 2024

 Some functions I miss. I brought to Py
 mgd 2024-04-09--27
 mgd 2025-02-04

 """

# cSpell:ignore latin CCITT

import os, time, platform
from sys import argv
from datetime import datetime
from typing import Any, Type, Tuple, List

from ..common.app_constants import APP_NAME


# https://docs.python.org/3/library/platform.html#platform.system
OS_NAME_IS = platform.system()
OS_IS_WINDOWS = OS_NAME_IS == "Windows"
OS_IS_LINUX = OS_NAME_IS == "Linux"
OS_IS_MAC = OS_NAME_IS == "Darwin"


def get_envvar_prefix() -> str:
    return f"{APP_NAME}_".upper()


def get_envvar(name: str, default: str = "") -> str:
    value = "" if is_str_none_or_empty(name) else os.getenv(f"{get_envvar_prefix()}{name}")
    return default if is_str_none_or_empty(value) else value


def now() -> datetime:
    # current date time
    return datetime.now()


def as_str_strip(s: str) -> str:
    return (str(s) + "").strip()


def quote(s: str, always: bool = True) -> str:
    """
    Args:
        s: The string to be quoted.
        always: If True, always enclose the string in double quotes (not only if it contains spaces).
    Returns:
        - s, with escaped double quotes (\"),
          and
        - enclosed in double quotes if:
            - it contains one or more spaces
              or
            - if always is True.
    """
    quoted = to_str(s)
    if '"' in quoted:
        quoted = quoted.replace('"', '\\"')

    if not always and " " not in quoted:
        return s

    quoted = quoted.replace(" ", "_")

    return f'"{quoted}"'


def is_str_none_or_empty(s: str) -> bool:
    """
    Returns True if the argument is None, not a str, or an empty (only spaces, \n, \t, etc) string
    """
    # até 2024-11-13 (Boa sorte!) return (s is None) or (as_str_strip(s) == "")
    return (s is None) or not isinstance(s, str) or (as_str_strip(s) == "")


def is_list_none_or_empty(list: List) -> bool:
    """
    Returns True if the argument is None, not a List, or an empty List
    """
    return (list is None) or not isinstance(list, list) or len(list) == 0


def get_init_params(from_instance: Any, From_class=None) -> dict:
    """
    Copies parameters from an instance based on the __init__ method of its class.

    Args:
        from_instance: The instance to copy attribute values from.

    Returns:
        A dictionary containing parameters that match the __init__ method.
    """
    import inspect

    # #
    # if not isinstance(from_instance, From_class):
    #     raise TypeError(f"Expected instance of {From_class} got {type(from_instance)}.")

    From_Class = type(from_instance)
    init_signature = inspect.signature(From_Class.__init__)

    # Get parameter names, excluding 'self'
    init_params = [param_name for param_name in init_signature.parameters if param_name != "self"]

    params = {
        param_name: getattr(from_instance, param_name)
        for param_name in init_params
        if hasattr(from_instance, param_name)
    }

    return params


def to_int(s: str, default=-1) -> int:
    """
    Returns the argument as a integer or default if not a valid int
    """
    try:
        return int(s)
    except ValueError:
        return default


def to_str(s: str) -> str:
    """
    Returns the argument as a string, striping spaces
    """
    return "" if is_str_none_or_empty(s) else as_str_strip(s)


# initialize special attributes
def as_bool(val: Any, val_if_none: bool | None = False) -> bool:
    # fmt: off
    return (val_if_none if val is None else str(val).lower() in ["1", "t", str(True).lower(),])
    # fmt: on


def strip_and_ignore_empty(s: str, sep=",", max_split=-1) -> list[str]:
    """
    Returns a list of the striped items created by splitting s and ignoring empty items
    """
    result = []
    for item in (i.strip() for i in to_str(s).split(sep, max_split) if i.strip()):
        if not is_str_none_or_empty(item):
            result.append(item)

    return result


def camel_to_snake(string: str) -> str:
    """Converts a camel case string to snake case.

    Args:
      string: The camel case string to convert.

    Returns:
      The converted snake case string.
    """
    snake_case = ""
    for char in string:
        snake_case += ("_" if char.isupper() else "") + char.lower()

    return snake_case.strip("_")  # Remove leading underscores


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

    if data is None:
        return 0
    elif type(data) == bytes:
        pass
    elif not isinstance(data, str):
        raise TypeError("Expecting bytes of str parameter.")
    elif is_str_none_or_empty(data):
        return 0
    else:  # Convert string to bytes
        data = data.encode()

    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1

            crc &= 0xFFFF

    return crc


# def current_milliseconds():
def ms_since_epoch():
    """
    milliseconds since the last Unix epoch (January 1, 1970, 00:00:00 UTC).
    """
    return time.time_ns() // 1_000_000


def ms_since_midnight(toBase22: bool) -> int | str:
    """
    max -> d86400000 -> x526 5C00 -> (22)ggi.48g
    """
    today = datetime.now()
    midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)
    time_delta = today - midnight
    ms = int((time_delta.total_seconds() * 1000) + (time_delta.microseconds / 1000))
    return to_base(ms, 22).zfill(6) if toBase22 else ms


def to_base(number: int, base: int) -> str:
    if base < 2 or base > 36:
        raise ValueError("Base must be between 2 and 36.")

    result = ""
    if number == 0:
        result = "0"
    elif base == 2:
        result = format(number, "b")
    elif base == 8:
        result = format(number, "o")
    elif base == 16:
        result = format(number, "x")
    else:
        base_digits = "0123456789abcdefghijklmnopqrstuvwxyz"[:base]  # Digits for the specified base
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
    if std_text is None or std_text == b"":
        return ""

    try:
        # Try UTF-8 first, as it's commonly used
        return std_text.decode("utf-8")
    except UnicodeDecodeError:
        # If UTF-8 fails, try common encodings for Windows and latin-1
        for encoding in ("latin-1", "cp1252"):
            try:
                return std_text.decode(encoding)
            except Exception:
                pass

    # If all encodings fail, return the raw bytes as a string
    return str(std_text)


def set_flags_from_argv(obj):
    """
    Sets instances attributes based on command-line arguments.

    Iterates over the obj attributes and checks if their corresponding flags
    are present in `sys.argv`. If a flag is found, the attribute is set to `True`.
    """
    for attr in dir(obj):
        flag = f"--{attr}"
        # param = f"-{attr}"
        if attr.startswith("_"):
            pass  # Skip private attributes
        elif any(f.lower() == flag.lower() for f in argv) if OS_IS_WINDOWS else (flag in argv):
            setattr(obj, attr, True)
        # elif any(f.lower() == param.lower() for f in argv) if OS_IS_WINDOWS else (param in argv):
        # TODO: setattr(obj, attr, attr++)

    return obj


class EmptyClass:
    pass


def copy_attributes(class_instance: Any, this_types: Tuple[Type] | Type = None) -> EmptyClass:
    """
    Copies the specified simple type attributes from a class_instance,
    of the ones specified in the second argument or the defaults

    Args:
        class_instance: The instance object copy attributes from.
        this_types: An optional type to add to the list of included types or a
            Tuple of types to use instead of the default list

    Returns:
        A dictionary containing the copied attributes.
    """

    default_types = (str, int, float, bool, datetime)

    if this_types is None:
        valid_types = default_types
    elif isinstance(this_types, type):
        valid_types = default_types + (this_types,)
    elif isinstance(this_types, tuple):
        valid_types = this_types

    copy_instance = EmptyClass()
    for key, value in class_instance.__dict__.items():
        if isinstance(value, valid_types):
            setattr(copy_instance, key, value)

    return copy_instance


# eof
