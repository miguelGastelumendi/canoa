"""*app_context_vars*

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


-- [⚠️] -------
    Avoid calling any of these functions in `main.py` or `carranca.__init__.py`
    as there is no `has_request_context` and a sidekick is already running.



Equipe da Canoa -- 2025
mgd


"""

# cSpell:ignore mgmt sepsusr usrlist

from flask import has_request_context, g
from typing import Callable, Optional, Any
from flask_login import current_user
from werkzeug.local import LocalProxy

from carranca import global_sidekick
from .Sidekick import Sidekick
from ..private.AppUser import AppUser
from ..private.UserSep import user_seps_rtn, user_sep_dict, user_sep_list
from ..private.JinjaUser import JinjaUser
from ..helpers.types_helper import error_message

# share global sidekick
sidekick: Sidekick = global_sidekick


# local lock control
from threading import Lock

_locks = {}
_locks_lock = Lock()
RUN_WITH_LOCKS = True  # debug _get_scoped_var


def _get_scoped_var(var_name: str, do_var_creator: Callable[[], Any]) -> Optional[Any]:
    """
    Returns a value, from the current request context (g) under the var_name , creating it if necessary.
    """

    if not has_request_context():  # no g
        raise RuntimeError(f"Request context is required to retrieve `{var_name}`.")

    _CREATION_FAILED = object()

    var_value = None
    if RUN_WITH_LOCKS:
        with _locks_lock:
            if var_name not in _locks:
                _locks[var_name] = Lock()

        with _locks[var_name]:
            if hasattr(g, var_name):
                var_value = getattr(g, var_name)
                print(f"{var_name} data found, using sema.")
                if var_value is _CREATION_FAILED:
                    raise RuntimeError(
                        f"Previous attempt to create `{var_name}` failed."
                    )
                return var_value
            else:
                try:
                    var_value = do_var_creator()
                    if var_value is None:
                        raise ValueError(...)
                    setattr(g, var_name, var_value)
                    return var_value
                except Exception as e:
                    setattr(g, var_name, _CREATION_FAILED)
                    raise RuntimeError(
                        f"Scoped variable creator {do_var_creator} raised an exception [{e}]."
                    )

    elif not hasattr(g, var_name):
        try:
            var_value = do_var_creator()
            if var_value is None:
                raise ValueError(f"{do_var_creator} returned None for `{var_name}`.")
            setattr(g, var_name, var_value)
        except Exception as e:
            raise RuntimeError(
                f"Scoped variable creator {do_var_creator} raised an exception [{e}]."
            )

        return var_value
    else:
        var_value = getattr(g, var_name)
        print(f"{var_name} data found.")
        return var_value


# App User
# -----------
def _get_app_user() -> Optional[AppUser]:
    from ..helpers.pw_helper import is_someone_logged

    """
    Info of the logged user or None if no one is logged
    """
    if is_someone_logged():
        return _get_scoped_var("_app_user", AppUser)
    else:
        return None


# Jinja User (few attributes, as this user is exposed to HTML files via Jinja)
# --------------
def _get_jinja_user() -> Optional[JinjaUser]:
    def _do_jinja_user() -> JinjaUser:
        return JinjaUser(_get_app_user())

    jinja_user = _get_scoped_var("_jinja_user", _do_jinja_user)

    return jinja_user


count: int = 0


# User SEPs
# -----------
def _prepare_user_seps(direct=False) -> user_seps_rtn:
    from ..models.private import MgmtSepsUser
    from ..private.UserSep import UserSep
    from ..private.sep_icon import do_icon_get_url
    from ..helpers.pw_helper import is_someone_logged
    from ..helpers.py_helper import class_to_dict

    user_id: int = current_user.id if is_someone_logged() else -1

    global count
    count += 1
    try:
        _debug = direct or count > 1
        if _debug:
            print(f"Count: {count} in")

        try:
            sidekick.display.debug("user_sep start creation...")
            sep_usr_rows = MgmtSepsUser.get_user_sep_list(user_id)
        except Exception as e:
            return str(e)

        seps: list[user_sep_dict] = []
        for sep_row in sep_usr_rows:
            item = UserSep(**sep_row)
            item.icon_url = do_icon_get_url(item.icon_file_name, item.id)
            dic = class_to_dict(
                item
            )  # as `g` only saves 'simple' classes convert it to a Dict
            seps.append(dic)

    finally:
        sidekick.display.debug("user_sep was created.")
        # global count
        count -= 1
        if _debug:
            print(f"Count: {count} out")

    return seps


def _get_user_seps() -> user_seps_rtn:
    from ..private.UserSep import UserSep

    if app_user is None:
        result: error_message = "No current user to retrieve SEP data."
    else:  # convert simple dict to UserSep again
        list_dic = _get_scoped_var("_user_seps", _prepare_user_seps)
        if list_dic is None or not isinstance(list_dic, list):
            sidekick.display.error(
                f"An error occurred getting sep from user {app_user.id}: [{type(list_dic)}] → {list_dic}."
            )
            result = []
        else:
            result: user_sep_list = [UserSep(**item) for item in list_dic]

    return result


# =========================================================
# Proxies
# =========================================================

app_user: AppUser = LocalProxy(_get_app_user)


jinja_user: Optional[JinjaUser] = LocalProxy(_get_jinja_user)


user_seps: user_seps_rtn = LocalProxy(_get_user_seps)

# eof
