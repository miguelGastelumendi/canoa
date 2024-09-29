"""
 Equipe da Canoa -- 2024

 Simple colored print to screen

 mgd 2024-04-09--27

 """

# cSpell:ignore

from enum import Enum

class Display:
    class Color(Enum):
        NONE = 0
        INFO = 1
        WARN = 2
        ERROR = 3

    def code(color: str):
        return "\033[" + ("" if color is None else f"{color}m")

    colors = ["", code("38;5;120"), code("93"), code("91")]
    end_color = code(0)
    ESC = code(None)

    def print(dColor: Color, msg: str, start_with: str = "") -> None:
        endColor = "" if dColor == Display.Color.NONE else Display.end_color
        print(f"{start_with}{Display.colors[dColor.value]}{msg}{endColor}")

    def show(msg: str, start_with: str = "") -> None:
        Display.print(Display.Color.NONE, msg, start_with)

    def info(msg: str, start_with: str = "") -> None:
        Display.print(Display.Color.INFO, msg, start_with)

    def warn(msg: str, start_with: str = "") -> None:
        Display.print(Display.Color.WARN, msg, start_with)

    def error(msg: str, start_with: str = "") -> None:
        Display.print(Display.Color.ERROR, msg, start_with)


# if __name__ == "__main__":
#    Display.print(Display.Color.NONE, 'Nada')
#    Display.print(Display.Color.INFO, 'info')
#    Display.print(Display.Color.WARN, 'warning')
#    Display.print(Display.Color.ERROR, 'Error')
#    Display.info('informação')

#eof