

import re

def ansi_to_html(ansi_text):
    # Define ANSI escape code to CSS mapping
    ansi_css_mapping = {
        "0": "",         # Reset all attributes
        "1": "font-weight: bold;",  # Bold
        "30": "color: black;",      # Black
        "31": "color: red;",        # Red
        "32": "color: green;",      # Green
        "33": "color: yellow;",     # Yellow
        "34": "color: blue;",       # Blue
        "35": "color: magenta;",    # Magenta
        "36": "color: cyan;",       # Cyan
        "37": "color: white;",      # White
    }

    # Convert ANSI escape codes to HTML/CSS
    html_text = ""
    in_escape_code = False
    escape_code = ""
    for char in ansi_text:
        if char == "\x1b":
            in_escape_code = True
            escape_code = ""
        elif in_escape_code and char.isdigit():
            escape_code += char
        elif in_escape_code and char == "m":
            # End of escape sequence
            css_styles = []
            for code in escape_code.split(";"):
                if code in ansi_css_mapping:
                    css_styles.append(ansi_css_mapping[code])
            html_text += '<span style="{}">'.format(";".join(css_styles))
            in_escape_code = False
        elif char == "\n":
            html_text += "<br>"
        elif char == "\r":
            html_text += ""
        else:
            html_text += char

    # Close any open span tag
    if in_escape_code:
        html_text += '</span>'

    return html_text


# Example ANSI text
# ansi_text = "\x1b[37m\x1b[1mNúmero de erros: 0\x1b[33m\x1b[1mNúmero de avisos: 3\x1b[34m\x1b[1m\nTempo total de execução: 4.1 segundos\x1b[0m"

# Convert ANSI text to HTML
# html_text = ansi_to_html(ansi_text)

# print(html_text)
