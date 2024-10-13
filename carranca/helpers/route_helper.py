# Equipe da Canoa -- 2024
# scripts\routes_helpers.py
#
# Python functions to assist routes.py
#
# mgd 2024-05-13
# cSpell:ignore werkzeug tmpl

import requests
from os import path
from typing import Tuple, Any
from flask import redirect, request, url_for
from .py_helper import is_str_none_or_empty, camel_to_snake, to_str
from ..main import shared

base_route_private = "private"
base_route_public = "public"
public_route__password_reset = "password_reset"
templates_found = []

def _route(base: str, page: str, **params) -> str:
    address = f"{bp_name(base)}.{page}"
    return url_for(address, **params)


def bp_name(base: str) -> str:
    return f"bp_{base}"


def private_route(page: str, **params) -> str:
    return _route(base_route_private, page, **params)


def public_route(page: str, **params) -> str:
    return _route(base_route_public, page, **params)


def login_route() -> str:
    return public_route("login")


def register_route() -> str:
    """
    The `register` page can converts,
    a visitor into a user.
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


def _get_form_data(section: str, file: str, folder: str) -> Tuple[str, bool, dict[str, str]]:
    from .ui_texts_helper import get_section

    file = camel_to_snake(section) if file is None else file
    file_name = f"{file}.html.j2"
    # template *must* be with '/':
    template = f"./{folder}/{file_name}"
    full_name = path.join(".", shared.config.TEMPLATES_FOLDER, folder, file_name)
    if full_name in templates_found:
        pass
    elif path.isfile(full_name):
        templates_found.append(full_name)
    else:
        raise FileNotFoundError(f"The requested template '{full_name}' was not found.")
    is_get = is_method_get()
    texts = get_section(section)
    return template, is_get, texts


def get_private_form_data(section: str, file: str = None) -> Tuple[str, bool, dict[str, str]]:
    return _get_form_data(section, file, base_route_private)


def get_account_form_data(section: str, file: str = None) -> Tuple[str, bool, dict[str, str]]:
    return _get_form_data(section, file, "accounts")


def init_form_vars() -> Tuple[Any, str, bool, dict[str, str]]:
    return None, "", True, {}


def redirect_to(route: str, message: str = None) -> str:
    # TODO: display message 'redirecting to ...
    return redirect(route)

from ..config import BaseConfig
def is_external_ip_ready(app_config: BaseConfig) -> bool:
    if is_str_none_or_empty(app_config.SERVER_EXTERNAL_IP):
        try:
            app_config.SERVER_EXTERNAL_IP = requests.get(app_config.EXTERNAL_IP_SERVICE).text.strip()
        except:
            # LOG
            app_config.SERVER_EXTERNAL_IP = ""

    return not is_str_none_or_empty(app_config.SERVER_EXTERNAL_IP)


# eof
