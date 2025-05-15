"""
Python functions to assist routes.py

mgd 2024-05-13
Equipe da Canoa -- 2024
"""

# cSpell:ignore werkzeug tmplt

import requests
from os import path
from typing import Tuple, Optional
from flask import redirect, request, url_for

from .py_helper import is_str_none_or_empty, camel_to_snake, clean_text
from .html_helper import URL_PATH_SEP
from .types_helper import ui_db_texts, template_file_full_name
from .ui_db_texts_helper import UITextsKeys, get_form_texts

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


def is_method_get() -> bool:
    """
    Determine if the current request method is GET.
    Raises a ValueError for unexpected request methods.
    """
    rm = request.method.upper()
    is_get = rm == "GET"
    if is_get:
        pass
    elif rm == "POST":
        is_get = False
    else:
        raise ValueError(f"Unexpected request method: '{rm}'.")

    return is_get


def get_input_text(name: str, not_allowed: Optional[str] = "") -> str:
    text = request.form.get(name)
    # 2025.05.13 return to_str(text)
    return clean_text(text, not_allowed)


def get_template_name(tmplt: str, folder: str) -> template_file_full_name:
    from ..common.app_context_vars import sidekick

    tmplt_file_name = f"{tmplt}.html.j2"
    # template *must* be with '/':
    template: template_file_full_name = f".{URL_PATH_SEP}{folder}{URL_PATH_SEP}{tmplt_file_name}"
    tmplt_full_name = path.join(".", sidekick.config.TEMPLATES_FOLDER, folder, tmplt_file_name)
    if tmplt_full_name in templates_found:
        pass
    elif path.isfile(tmplt_full_name):
        templates_found.append(tmplt_full_name)
    else:
        raise FileNotFoundError(f"The requested template '{tmplt_full_name}' was not found.")

    return template


def _get_form_data(
    section: str, tmplt: str, folder: str
) -> Tuple[template_file_full_name, bool, ui_db_texts]:

    tmplt = camel_to_snake(section) if tmplt is None else tmplt
    template: template_file_full_name = get_template_name(tmplt, folder)
    is_get = is_method_get()

    # a section of ui_itens
    ui_texts = get_form_texts(section)
    if is_get:
        ui_texts[UITextsKeys.Msg.error] = ""  # This is a Cache BUG to
    else:
        ui_texts[UITextsKeys.Msg.info] = ""  # only GET has info

    return template, is_get, ui_texts


def get_private_form_data(
    section: str, tmplt: str = None
) -> Tuple[template_file_full_name, bool, ui_db_texts]:
    return _get_form_data(section, tmplt, base_route_private)


def get_account_form_data(
    section: str, tmplt: str = None
) -> Tuple[template_file_full_name, bool, ui_db_texts]:
    return _get_form_data(section, tmplt, "accounts")


def init_form_vars() -> Tuple[dict, template_file_full_name, bool, ui_db_texts]:
    # tmplt_form, template, is_get, ui_texts
    return {}, "", True, {}


def redirect_to(route: str, message: str = None) -> str:
    # TODO: display message 'redirecting to ...
    return redirect(route)


def is_external_ip_ready(config: BaseConfig) -> bool:

    if is_str_none_or_empty(config.SERVER_EXTERNAL_IP):
        try:
            config.SERVER_EXTERNAL_IP = requests.get(config.EXTERNAL_IP_SERVICE).text.strip()
        except:
            # TODO: LOG
            config.SERVER_EXTERNAL_IP = ""

    return not is_str_none_or_empty(config.SERVER_EXTERNAL_IP)


# eof
