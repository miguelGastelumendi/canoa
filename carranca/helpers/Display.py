"""
 Equipe da Canoa -- 2024

 Simple colored print to screen

 mgd 2024-09-27

 """

# cSpell:ignore

from enum import Enum
from .py_helper import is_enum_of_type, is_str_none_or_empty


class Display:
    class Kind(Enum):
        SIMPLE = 0
        INFO = 1
        WARN = 2
        ERROR = 3
        DEBUG = 4

    def __init__(self, prompt: str= '', debug_output: bool = False ):
        Display.default_prompt = prompt
        Display.debug_output = debug_output

    def code(color: str):
        return '\033[' + ('' if color is None else f'{color}m')

    # https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
    #             Info green, Warn yellow Error red   Debug Cyan
    colors = ['', code('32'), code('33'), code('31'), code('36')]
    end_color = code(0)
    ESC = code(None)
    debug_output = False
    default_prompt = ''

    @staticmethod
    def print(kind_or_color: Kind | str, msg: str, prompt: str = None) -> None:
        none_color = Display.colors[Display.Kind.SIMPLE.value]
        start_color = none_color
        if is_str_none_or_empty(msg):
            return
        elif isinstance(kind_or_color, str):
            start_color = kind_or_color
        elif not is_enum_of_type(kind_or_color, Display.Kind):
            return
        elif kind_or_color.value == Display.Kind.DEBUG.value and not Display.debug_output:
            return
        else:
            kind = kind_or_color.value
            start_color = Display.colors[kind]

        end_color = none_color if start_color == none_color else Display.end_color
        start_text = Display.default_prompt if prompt is None else prompt
        print(f"{start_text}{start_color}{msg}{end_color}")

    def simple(msg: str, prompt: str = None) -> None:
        Display.print(Display.Kind.SIMPLE, msg, prompt)

    def info(msg: str, prompt: str = None) -> None:
        Display.print(Display.Kind.INFO, msg, prompt)

    def warn(msg: str, prompt: str = None) -> None:
        Display.print(Display.Kind.WARN, msg, prompt)

    def error(msg: str, prompt: str = None) -> None:
        Display.print(Display.Kind.ERROR, msg, prompt)

    def debug(msg: str, prompt: str = None) -> None:
        Display.print(Display.Kind.DEBUG, msg, prompt)


# if __name__ == "__main__":
#     print('\n\nClass print:')
#     for e in Display.Kind:
#         Display.print(e, e.name)

#     print('\nPrint by line:')
#     Display.simple('simple')
#     Display.info('[i] info')
#     Display.warn('/\ warning/|')
#     Display.error('! error')
#     Display.debug('d Debug')
#     print(f"debug output is [{Display.debug_output}].")


#     print('\nInstance for canoa with debug output active:')
#     display = Display('Canoa: ', True)
#     print(f"debug output is [{Display.debug_output}].")
#     for e in Display.Kind:
#         display.print(e, e.name)

#     print('\nTest end')
#     Display.info('The end')


# eof
