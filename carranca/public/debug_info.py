"""
    Debug Info
    Debug information

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore sqlalchemy

import sqlalchemy
import platform
import flask
import importlib.metadata
from ..shared import app_config
from ..helpers.Display import Display
from ..helpers.py_helper import coalesce


def get_debug_info(bPrint: bool = False) -> dict:
    """App & and main packages version"""
    result = {}
    kl = 0
    vl = 0

    def _add(key, value):
        nonlocal kl, vl # int, float, bool, str, tuples... are immutables
        kl = len(key) if kl < len(key) else kl
        v= str(value)
        vl = len(v) if vl < len(v) else vl
        result[key] = v

    _add(f"{app_config.APP_NAME} Basic Configuration", "")
    _add("Version", app_config.APP_VERSION)
    _add("DEBUG", app_config.DEBUG)
    _add("Page Compression", app_config.APP_MINIFIED)
    _add("App root folder", app_config.ROOT_FOLDER)
    _add("Database address", app_config.SQLALCHEMY_DATABASE_URI)
    _add("Server address", app_config.SERVER_ADDRESS)
    _add(
        "External address ", coalesce(app_config.SERVER_EXTERNAL_IP, "<set on demand>")
    )
    _add("External port", coalesce(app_config.SERVER_EXTERNAL_PORT, "<none>"))

    _add("Versões dos Principais Pacotes", "")
    _add("Python", platform.python_version())
    _add("SQLAlchemy", sqlalchemy.__version__)
    _add("Flask", flask.__version__)
    _add("Jinja2", importlib.metadata.version("jinja2"))

    if bPrint:
        for key, value in result.items():
            c, v = (Display.Color.NONE, ': ' + value) if value else (Display.Color.INFO, '_' * vl)
            Display.print(c, f"{key.rjust(kl)}{v}")

    return result
#eof