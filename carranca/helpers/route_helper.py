"""
    Python functions to assist routes.py

    mgd 2024-05-13
    Equipe da Canoa -- 2024
"""

# cSpell:ignore werkzeug tmplt

import requests
from os import path
from typing import Tuple, Any
from flask import redirect, request, url_for
from .py_helper import is_str_none_or_empty, camel_to_snake, to_str
from .hints_helper import UI_Texts
from ..config import BaseConfig

base_route_private = "private"
base_route_public = "public"
base_route_static = "static"
public_route__password_reset = "password_reset"
templates_found = []

"""
  ## Dynamic Route:
  @bp_public.route("/docs/<publicDocName>")
  can handle multiple URLs by capturing the part after /docs/ as a parameter.

  ## Static Route:
  bp_public = Blueprint('bp_public', __name__, url_prefix='/docs')
  @bp_public.route('/privacyPolicy') handles a specific URL /docs/privacyPolicy.

"""


def _route(base: str, page: str, **params) -> str:
    address = f"{bp_name(base)}.{page}"
    url = url_for(address, **params)
    return url


def bp_name(base: str) -> str:
    return f"bp_{base}"


def private_route(page: str, **params) -> str:
    return _route(base_route_private, page, **params)


def public_route(page: str, **params) -> str:
    return _route(base_route_public, page, **params)


def static_route(filename: str) -> str:
    return url_for(base_route_static, filename=filename)


def login_route() -> str:
    return public_route("login")


def register_route() -> str:
    """
    The `register` page can convert,
    a visitor into a user.
    Anyone can be (requested)
    """
    return public_route("register")


def index_route() -> str:
    return public_route("index")


def home_route() -> str:
    return private_route("home")


def is_method_get() -> bool:  # raise error
    # mgd 2024.03.21
    is_get = True
    if request.method.upper() == "POST":
        is_get = False
    elif not is_get:
        # if not is_get then is_post, there is no other possibility
        raise ValueError("Unexpected request method.")

    return is_get


def get_input_text(name: str) -> str:
    text = request.form.get(name)
    return to_str(text)


def _get_form_data(section: str, tmplt: str, folder: str) -> Tuple[str, bool, UI_Texts]:
    from ..common.app_context_vars import sidekick
    from .ui_texts_helper import get_section

    tmplt = camel_to_snake(section) if tmplt is None else tmplt
    tmplt_file_name = f"{tmplt}.html.j2"
    # template *must* be with '/':
    template = f"./{folder}/{tmplt_file_name}"
    tmplt_full_name = path.join(".", sidekick.config.TEMPLATES_FOLDER, folder, tmplt_file_name)
    if tmplt_full_name in templates_found:
        pass
    elif path.isfile(tmplt_full_name):
        templates_found.append(tmplt_full_name)
    else:
        raise FileNotFoundError(f"The requested template '{tmplt_full_name}' was not found.")

    is_get = is_method_get()
    # a section of ui_itens
    ui_texts = get_section(section)
    return template, is_get, ui_texts


def get_private_form_data(section: str, tmplt: str = None) -> Tuple[str, bool, UI_Texts]:
    return _get_form_data(section, tmplt, base_route_private)


def get_account_form_data(section: str, tmplt: str = None) -> Tuple[str, bool, UI_Texts]:
    return _get_form_data(section, tmplt, "accounts")


def init_form_vars() -> Tuple[Any, str, bool, UI_Texts]:
    # tmplt_form, template, is_get, ui_texts
    return None, "", True, {}


def redirect_to(route: str, message: str = None) -> str:
    # TODO: display message 'redirecting to ...
    return redirect(route)


def is_external_ip_ready(config: BaseConfig) -> bool:

    if is_str_none_or_empty(config.SERVER_EXTERNAL_IP):
        try:
            config.SERVER_EXTERNAL_IP = requests.get(config.EXTERNAL_IP_SERVICE).text.strip()
        except:
            # LOG
            config.SERVER_EXTERNAL_IP = ""

    return not is_str_none_or_empty(config.SERVER_EXTERNAL_IP)


# eof
