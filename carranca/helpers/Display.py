"""
 Equipe da Canoa -- 2024

 Simple colored print to screen

 mgd 2024-09-27

 """

# cSpell:ignore

import time
from enum import Enum
from typing import List
from datetime import datetime
from .py_helper import is_str_none_or_empty


class Display:
    class Default:
        def __init__(
            self,
            prompt="",
            mute=False,
            debug_output=False,
            icon_output=True,
            colors=None,
            icons=None,
        ):
            self.prompt = prompt
            self.mute = mute
            self.debug_output = debug_output
            self.icon_output = icon_output
            self.colors = colors
            self.icons = icons

    class Kind(Enum):
        PROMPT = 0
        SIMPLE = 1
        INFO = 2
        WARN = 3
        ERROR = 4
        DEBUG = 5

    # https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters
    def code(color_code: int):
        #       reset                 return ESC only        valid Set foreground color code
        if not ((color_code == 0) or (color_code is None) or (color_code in range(30, 37))):
            ValueError("Invalid color code, valid values are in [30, 37].")

        return "\033[" + ("" if color_code is None else f"{color_code}m")

    no_color = ""
    reset_color = code(0)
    ESC = code(None)

    default = Default(
        # keep same order as Display.__init__
        "",
        False,
        False,
        True,
        [
            # https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit
            code(36),  # Prompt gray
            "",  # Simple, no color, default
            code(32),  # Info green
            code(33),  # Warn yellow
            code(31),  # Error red
            code(35),  # Debug Magenta
        ],
        [
            "",  # Prompt
            "",  # Simple
            "[i] ",  # Info
            "[▲] ",  # Warn
            "[!] ",  # Error
            "[¤] ",  # Debug
        ],
    )

    def debug_output() -> bool:
        return Display.default.debug_output

    def icon_output() -> bool:
        return Display.default.icon_output

    def __init__(
        self,
        # keep same order as Display.Default
        prompt: str = None,
        mute_all: bool = False,
        debug_output: bool = None,
        icon_output: bool = None,
        elapsed_from: float = None,
        colors: List[str] = None,
        icons: List[str] = None,
    ):
        _d = Display.default  # value is None => use default
        self.mute = True if mute_all else False
        self.prompt = _d.prompt if prompt is None else prompt
        self.debug_output = _d.debug_output if debug_output is None else debug_output
        self.icon_output = _d.icon_output if icon_output is None else icon_output
        self.elapsed_output = elapsed_from is not None
        self.elapsed_from = elapsed_from if self.elapsed_output else time.perf_counter()
        self.colors = _d.colors if colors is None else colors
        self.icons = _d.icons if icons is None else icons
        k_error = "Parameter '{0}' must be a list of Display.Kind items."
        if colors is not None and len(colors) != len(Display.Kind):
            raise ValueError(k_error.format("colors"))

        if icons is not None and len(icons) != len(Display.Kind):
            raise ValueError(k_error.format("icons"))

    def color(self, kind: Kind) -> str:
        return self.colors[kind.value]

    def print(
        self, kind_or_color: Kind | str, msg: str, prompt: str = None, icon_output: bool = None
    ) -> None:
        if self.mute:
            return

        start_color = Display.no_color
        is_kind = isinstance(kind_or_color, Display.Kind)
        kind = kind_or_color if is_kind else Display.Kind.SIMPLE.value
        if is_str_none_or_empty(msg):
            print(msg)  # perhaps a command
            return
        elif not (is_kind or (kind_or_color is None) or isinstance(kind_or_color, str)):
            return
        elif is_kind and (kind_or_color == Display.Kind.DEBUG) and not self.debug_output:
            return
        elif kind_or_color is None:
            start_color = Display.no_color
        elif is_kind:
            start_color = self.color(kind)
        else:
            start_color = Display.no_color if is_str_none_or_empty(kind_or_color) else kind_or_color

        _prompt = self.prompt if prompt is None else str(prompt)
        start_text = (
            ""
            if is_str_none_or_empty(_prompt)
            else f"{self.color(Display.Kind.PROMPT)}{_prompt}{Display.reset_color}"
        )
        _icon_output = self.icon_output if icon_output is None else bool(icon_output)

        icon = self.icons[kind.value] if _icon_output else ""
        end_color = Display.no_color if start_color == Display.no_color else Display.reset_color
        print(f"{start_text}{start_color}{icon}{msg}{end_color}")

    def simple(self, msg: str, prompt: str = None, icon_output: bool = None) -> None:
        self.print(Display.Kind.SIMPLE, msg, prompt, icon_output)

    def info(self, msg: str, prompt: str = None, icon_output: bool = None) -> None:
        self.print(Display.Kind.INFO, msg, prompt, icon_output)

    def warn(self, msg: str, prompt: str = None, icon_output: bool = None) -> None:
        self.print(Display.Kind.WARN, msg, prompt, icon_output)

    def error(self, msg: str, prompt: str = None, icon_output: bool = None) -> None:
        self.print(Display.Kind.ERROR, msg, prompt, icon_output)

    def debug(self, msg: str, prompt: str = None, icon_output: bool = None) -> None:
        self.print(Display.Kind.DEBUG, msg, prompt, icon_output)

    def set_prompt(self, value: str) -> str:
        p = self.prompt
        self.prompt = "" if is_str_none_or_empty(value) else str(value)
        return p

    def set_icon_output(self, value: bool) -> bool:
        b = self.icon_output
        self.icon_output = bool(value)
        return b

    def set_elapsed_output(self, value: bool, elapsed_from: float = None) -> bool:
        b = self.elapsed_output
        self.elapsed_output = bool(value)
        if elapsed_from is not None:
            self.elapsed_from = elapsed_from
        elif self.elapsed_output and elapsed_from is None:
            self.elapsed_from = time.perf_counter()

        return b


# if __name__ == "__main__":
#     Display().simple("a")
#     Display().simple("b")

#     print("\nClass print:")
#     for e in Display.Kind:
#         Display().print(e, e.name)

#     print("\nPrint by function:")
#     Display().simple("simple")
#     Display().info("info")
#     Display().warn("warning")
#     Display().error("error")
#     Display().debug("Debug")
#     print(f"Display().debug_output is [{Display.debug_output()}].")
#     print(f"Display().icon_output is [{Display.icon_output()}].")

#     print("\nInstance for `canoa` with 'debug_output` active:")
#     display = Display("Canoa: ", True, False)
#     print(f"display.debug_output is [{display.debug_output}].")
#     print(f"display.icon_output is [{display.icon_output}].")
#     for e in Display.Kind:
#         display.print(e, e.name)

#  eof
