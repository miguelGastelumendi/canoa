"""
    SEP Constants

    Equipe da Canoa -- 2024
    mgd 2024-11-15
"""

# cSpell: ignore mgmt tmpl wtforms werkzeug lightgray iacute

from os import path
from ..Sidekick import sidekick

SCHEMA_ICON_EXTENSION = "svg"
SCHEMA_ICON_FOLDER = "schema_icons"
SCHEMA_ICON_LOCAL_PATH = path.join(sidekick.app.static_folder, SCHEMA_ICON_FOLDER)
SCHEMA_ICON_URL = f"{SCHEMA_ICON_FOLDER}/{{0}}"
SCHEMA_ICON_EMPTY = "schema-empty.svg"
SCHEMA_ICON_DEFAULT = """
        <svg width="62" height="62" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="lightgray" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="black">Vaz&iacute;o</text>
        </svg>
        """

# eof
