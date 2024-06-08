# Equipe da Canoa -- 2024
# scripts\routes_helpers.py
#
# Python functions to assist routes.py
#
# mgd 2024-05-13
# cSpell:ignore werkzeug uploadfile tmpl

from flask import redirect, request, url_for
from .texts_helper import get_section
from .py_helper import to_str


base_route_private = 'private'
base_route_public = 'public'
public_route_reset_password = 'resetpassword'

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
    return public_route('login')

def register_route() -> str:
    """
    The `register` page can converts,
    a visitor into a user.
    """
    return public_route('register')

def index_route() -> str:
    return public_route('index')

def home_route() -> str:
    return private_route('home')

def is_method_get() -> bool: # raise error
    # mgd 2024.03.21
   is_get= True
   if request.method.upper() == 'POST':
      is_get= False
   elif not is_get:
      # if not is_get then is_post, there is no other possibility
      raise ValueError('Unexpected request method.')

   return is_get

def get_input_text(name: str) -> str:
    text = request.form.get(name)
    return to_str(text)

def get_form_data(section: str, file: str, folder: str): # -> str, bool, dict[str, str]:
    template = f'{folder}/{file}.html.j2'
    is_get= is_method_get()
    texts = get_section(section)
    return template, is_get, texts

def get_private_form_data(section: str, file: str = None): # -> str, bool, dict[str, str]:
    file = section if file is None else file
    return get_form_data(section, file, './private')

def get_account_form_data(section: str, file: str = None): # -> str, bool, dict[str, str]:
    file = section if file is None else file
    return get_form_data(section, file, './accounts')

def redirect_to(route: str, message: str = None) -> str:
    # TODO: display message 'redirecting to ...
    return redirect(route)


#eof