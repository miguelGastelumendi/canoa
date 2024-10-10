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


def get_debug_info(app, config) -> List[Tuple[str, str]]:
    from ..helpers.py_helper import coalesce, is_str_none_or_empty

    """App & and main packages version"""
    result = []
    ml = 0
    vl = 0

    def _add(name, value):
        nonlocal ml, vl  # int, float, bool, str, tuples... are immutables
        ml = len(name) if ml < len(name) else ml
        v = str(value)
        vl = len(v) if vl < len(v) else vl
        result.append((name, v))

    _add(f"{config.APP_NAME} Configuration", "")
    _add("Version", config.APP_VERSION)
    _add("Mode", config.APP_MODE)
    _add("Debug", config.APP_DEBUG)
    _add("Debug Messages", config.APP_DEBUG)

    _add("Page Compression", config.APP_MINIFIED)
    _add("App root folder", config.ROOT_FOLDER)
    _add("Database address", config.SQLALCHEMY_DATABASE_URI)
    _add("Server address", config.SERVER_ADDRESS)
    _add("External address ", coalesce(config.SERVER_EXTERNAL_IP, "<set on demand>"))
    _add("External port", coalesce(config.SERVER_EXTERNAL_PORT, "<none>"))

    _add("Versions of the main packages", "")
    _add("Python", platform.python_version())
    _add("SQLAlchemy", sqlalchemy.__version__)
    _add("Flask", flask.__version__)
    _add("Jinja2", importlib.metadata.version("jinja2"))

    _add("Flask", "")
    _add("Name", app.name)
    _add("DEBUG", app.debug)
    _add("TESTING", app.testing)
    _add("SECRET_KEY", ("" if is_str_none_or_empty(app.secret_key) else "*******"))
    _add("Root Path", app.root_path)
    _add("Template Folder", app.template_folder)
    _add("Static Folder", app.static_folder)

    _add("OS Path", os.getcwd())

    # if bPrint:
    #     for name, value in result:
    #         kind, v = (
    #             (shared.display.Kind.SIMPLE, ": " + value)
    #             if value
    #             else (shared.display.Kind.INFO, "_" * vl)
    #         )
    #         shared.display.print(kind, f"{name.rjust(ml)}{v}", "", False)


    # max_len_first = max(len(first) for first, _ in tuples)
    # max_len_second = max(len(second) for _, second in tuples)

    return result


# eof
