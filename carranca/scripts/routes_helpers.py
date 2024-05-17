# Equipe da Canoa -- 2024
# scripts\routes_helpers.py
#
# Python functions to assist routes.py
#
# mgd 2024-05-13
# cSpell: ignore werkzeug uploadfile tmpl

from flask import redirect, request, url_for
from .texts_helper import get_section
from .pw_helper import is_user_logged
from .py_helper import to_str


base_route_private = 'private'
base_route_public = 'public'


def _route(base: str, page: str) -> str:
    address = f"{bp_name(base)}.{page}"
    return url_for(address)

def bp_name(base: str) -> str:
    return f"bp_{base}"

def private_route(page: str) -> str:
    return _route(base_route_private, page)

def public_route(page: str) -> str:
    return _route(base_route_public, page)

def login_route() -> str:
    """
    The `login` page can be access by everyone,
    is *public*, display a Login form that serves
    as a Menu. It gave access to [forget-password],
    [register] and the usual documents.
    """
    return public_route('login')

def register_route() -> str:
    return public_route('register')

def index_route() -> str:
    """
    `index` page is like the 'home'
    page for a logged user:
    an empty page with the menu
    """
    return private_route('index')

def home_route() -> str:
    """
    `home` route can be access by everyone, is public.
    There is not home.html or template.
    If the user is:
      logged -> redirected to index.
      not logged -> redirected to login
    """
    return public_route('home')

def is_method_get() -> bool: # raise error
    # mgd 2024.03.21
   is_get= True
   if request.method == 'POST':
      is_get= False
   elif not is_get:
      # if not is_get then is_post, there is no other possibility
      raise ValueError('Unexpected request method.')

   return is_get

def get_input_text(name: str) -> str:
    text = request.form.get(name)
    return to_str(text)

def get_route_data(route: str, file: str = None) -> str:
    file = route if file is None else file
    template = f'accounts/{file}.html.j2'
    is_get= is_method_get()
    logged = is_user_logged()

    _route = None if logged else login_route()
    #redirect = '' if logged else " [User is not logged,  will be redirect to index (401)]"
    #logger(f'@{request.method.lower()}:/{route}{redirect}')
    texts = get_section(route)

    return template, is_get, _route, texts

def redirect_to(route: str, message: str = None) -> str:
    # TODO: display message 'redirecting to ...
    return redirect(route)


#eof