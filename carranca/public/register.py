# Equipe da Canoa -- 2024
# public\login.py
#
# mgd
# cSpell:ignore tmpl sqlalchemy
"""
    *Register*
    Part of Public Authentication Processes
"""
from flask import render_template, request
from typing import Any
from carranca import db

from ..helpers.texts_helper import add_msg_success, add_msg_error
from ..helpers.route_helper import get_account_form_data, get_input_text, public_route

from .forms import RegisterForm
from .models import Users


def do_register():
    def __exists_user_where(**kwargs: Any) -> bool:
        records = Users.query.filter_by(**kwargs)
        user = None if not records or records.count() == 0 else records.first()
        return user is not None

    template, is_get, texts = get_account_form_data("register")
    tmpl_form = RegisterForm(request.form)

    if is_get:  # is_post
        pass

    elif __exists_user_where(username_lower=get_input_text("username").lower()):
        add_msg_error("userAlreadyRegistered", texts) if user_record_to_update else ""

    elif __exists_user_where(email=get_input_text("email").lower()):
        add_msg_error("emailAlreadyRegistered", texts) if user_record_to_update else ""

    else:
        try:
            user_record_to_update = Users(**request.form)
            db.session.add(user_record_to_update)
            db.session.commit()
            add_msg_success("welcome", texts)
        except Exception as e:
            add_msg_error("registerError", texts) if user_record_to_update else ""
            # TODO Log

    return render_template(
        template,
        form=tmpl_form,
        **texts,
        public_route=public_route,
    )


# eof
