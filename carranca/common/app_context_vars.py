""" *app_context_vars*

    Request Context
    ---------------
    Contains the mechanisms to store and retrieve variables from Flask's g object.

    The `g` object is a global namespace for holding any data you want during the
    lifetime of a request.

    It is unique to each request and is used to store and share data across different
    parts of your application, such as between view functions, before/after
    request functions, and other request handlers.


    Application Context
    -------------------
    Contains a shortcut to the global sidekick object.


    -- [/!\] -------
        Avoid calling any of this functions on main.py or carranca.__init__.py
        there is no has_request_context and there is a
        sidekick running create in.



    Equipe da Canoa -- 2025
    mgd


"""

# cSpell:ignore

from flask import has_request_context, g
from typing import Callable, Any
from threading import Lock
from werkzeug.local import LocalProxy

from .. import sidekick as global_sidekick
from .Sidekick import Sidekick
from ..private.Logged_user import LoggedUser


# share global sidekick
sidekick: Sidekick = global_sidekick


# local lock control
_locks = {}


def _get_scoped_var(var_name: str, func_creator: Callable[[], Any]) -> Any | None:
    """
    Returns a variable from the current request context, creating it if necessary.
    """

    if not has_request_context():  # no g
        return None
    elif var_name not in _locks:  # lock it, thread safety
        _locks[var_name] = Lock()

    with _locks[var_name]:
        if not hasattr(g, var_name):
            setattr(g, var_name, func_creator())

    return getattr(g, var_name, None)


# variables getters
def _get_logged_user() -> LoggedUser | None:
    from ..helpers.pw_helper import is_someone_logged

    """
    Info of the logged user or None if no one is logged
    """
    if is_someone_logged():
        return _get_scoped_var("_logged_user", LoggedUser)
    else:
        return None


# Proxies

logged_user: LoggedUser | None = LocalProxy(_get_logged_user)


# eof
