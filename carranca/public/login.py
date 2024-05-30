# Equipe da Canoa -- 2024
# public\login.py
#
# mgd
# cSpell:ignore tmpl sqlalchemy
"""
    *Login*
    Part of Public Authentication Processes
"""
from flask import render_template, request
from flask_login import login_user
from sqlalchemy import or_

from ..helpers.py_helper import to_str
from ..helpers.pw_helper import internal_logout, someone_logged, verify_pass
from ..helpers.texts_helper import add_msg_error
from ..helpers.route_helper import get_account_form_data, get_input_text, home_route, private_route, public_route, redirect_to

from .forms import LoginForm
from .models import Users


def do_login():
    template, is_get, texts = get_account_form_data('login')
    tmpl_form = LoginForm(request.form)

    if is_get and someone_logged():
        internal_logout()

    elif is_get:
        pass

    else:
        username= get_input_text('username')
        password= get_input_text('password')
        search_for= to_str(username).lower()

        user= Users.query.filter(or_(Users.username_lower == search_for, Users.email == search_for)).first()
        if not user or not verify_pass(password, user.password):
            add_msg_error('userOrPwdIsWrong', texts)

        elif user.disabled:
            add_msg_error('userIsDisabled', texts)

        else:
            remember_me = to_str(request.form.get('remember_me')); # not always returns
            login_user(user, remember_me)
            return redirect_to(home_route())

    return render_template(
        template,
        form= tmpl_form,
        public_route= public_route,
        private_route= private_route,
        **texts
    )
#eof
