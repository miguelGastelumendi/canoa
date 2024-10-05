"""
    Debug Info
    Debug information

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore sqlalchemy
import os
import flask
import platform
import sqlalchemy
import importlib.metadata

from typing import List, Tuple
from ..helpers.py_helper import coalesce
from ..Shared import shared


def get_debug_info(bPrint: bool = False) -> List[Tuple[str, str]]:
    """App & and main packages version"""
    result = []
    ml = 0
    vl = 0
    cfg = shared.app_config

    def _add(name, value):
        nonlocal ml, vl  # int, float, bool, str, tuples... are immutables
        ml = len(name) if ml < len(name) else ml
        v = str(value)
        vl = len(v) if vl < len(v) else vl
        result.append((name, v))

    _add(f"{cfg.APP_NAME} Basic Configuration", "")
    _add("Version", cfg.APP_VERSION)
    _add("Mode", cfg.APP_MODE)
    _add("DEBUG", cfg.DEBUG)
    _add("TESTING", cfg.TESTING)
    _add("Page Compression", cfg.APP_MINIFIED)
    _add("App root folder", cfg.ROOT_FOLDER)
    _add("Database address", cfg.SQLALCHEMY_DATABASE_URI)
    _add("Server address", cfg.SERVER_ADDRESS)
    _add("External address ", coalesce(cfg.SERVER_EXTERNAL_IP, "<set on demand>"))
    _add("External port", coalesce(cfg.SERVER_EXTERNAL_PORT, "<none>"))

    _add("Versions of the main packages", "")
    _add("Python", platform.python_version())
    _add("SQLAlchemy", sqlalchemy.__version__)
    _add("Flask", flask.__version__)
    _add("Jinja2", importlib.metadata.version("jinja2"))

    _add("Flask", "")
    _add("Name", shared.app.name)
    _add("Root Path", shared.app.root_path)
    _add("Template Folder", shared.app.template_folder)
    _add("Static Folder", shared.app.static_folder)

    _add("OS Path", os.getcwd())

    if bPrint:
        b = shared.display.set_icon_output(False)
        for name, value in result:
            kind, v = (
                (shared.display.Kind.SIMPLE, ": " + value)
                if value
                else (shared.display.Kind.INFO, "_" * vl)
            )
            shared.display.print(kind, f"{name.rjust(ml)}{v}", "")
        shared.display.set_icon_output(b)

    return result


# eof
