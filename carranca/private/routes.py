"""
*Routes*
Private Routes
This routes are private, users _must be_ logged

Equipe da Canoa -- 2024
mgd
"""

# cSpell: ignore werkzeug wtforms tmpl mgmt jscmd
import errno
from carranca.helpers.db_helper import retrieve_dict
from flask import Blueprint, request
from flask_login import login_required, current_user

from typing import Tuple, Callable

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import internal_logout, nobody_is_logged
from ..public.ups_handler import ups_handler
from ..helpers.uiact_helper import UiActResponse, UiActResponseProxy, UiActResponseKeys
from ..helpers.jinja_helper import process_template
from ..helpers.types_helper import jinja_template, json_txt
from ..helpers.js_consts_helper import js_form_cargo_id, js_form_sec_check
from ..helpers.route_helper import (
    get_private_response_data,
    base_route_private,
    private_route,
    get_method,
    is_method_get,
    login_route,
    redirect_to,
    bp_name,
    MTD_ANY,
    MTD_GET,
    MTD_POST,
)

# === module variables ====================================
bp_private = Blueprint(bp_name(base_route_private), base_route_private, url_prefix="")


# === Test _ route ========================================
@bp_private.route("/test_route")
def test_route():
    return


# === routes =============================================
@bp_private.route("/home")
def home():
    """
    `home` page is the _landing page_
     for *users* (logged visitors).

    It displays the main menu.
    """

    if nobody_is_logged():
        return redirect_to(login_route(), None)

    template, _, texts = get_private_response_data("home")
    return process_template(template, **texts)


@login_required
@bp_private.route("/sep_mgmt", methods=MTD_ANY)
def sep_mgmt():
    """
    Through this route, the admin user can manage which
    user is the manager of a SEP

    """
    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .sep_mgmt.sep_mgmt import sep_mgmt

        return sep_mgmt()

#  TODO: Virou marmelada... redo it
# def grid_route(code: str, action_route: str, action_show: Callable, method: str = MTD_GET):
#     """
#     This func routes calls from a grid or to a grid. 8—|
#     see sep_grid & scm_grid
#     """

#     from ..helpers.uiact_helper import GridAction, GridCargoKeys, GridResponse

#     error = "Invalid route found."
#     try:
#         def _goto(item_code: str) -> str:
#             url = private_route(action_route, code=item_code)
#             return redirect_to(url)

#         def _get_route_error(param: str) -> str:
#             return f"Unexpected route parameter [{param}]."

#         error = _get_route_error("?")
#         if nobody_is_logged():
#             return redirect_to(login_route())
#         elif (method != request.method.upper()):
#             error = _get_route_error(method)
#         \
#             return action_show()
#         elif method == MTD_GET and code != js_form_cargo_id:
#             error = _get_route_error(code)
#         elif not is_str_none_or_empty(msg_error:= js_form_sec_check()):
#             error = msg_error
#         elif is_str_none_or_empty(cmd_text := request.args.get(js_form_cargo_id, "") if method == MTD_GET else request.form.get(js_form_cargo_id)):
#             error = _get_route_error("empty")
#         else:
#             error = _get_route_error("jscmd")
#             grid_response = GridResponse(cmd_text)
#             action = grid_response.action
#             error = _get_route_error(f"action: {action}")
#             match action:
#                 case GridCargoKeys.insert:
#                     return _goto(GridAction.add)
#                 case GridCargoKeys.edit:
#                     data = grid_response.do_data()
#                     return _goto(data)
#                 case GridCargoKeys.save:
#                     data = grid_response.do_data()
#                     return _goto(data)
#                 case GridCargoKeys.delete:
#                     error = "The Delete procedure is still under development."
#                     # TODO Remove all
#                     pass
#     except Exception e:
#         msg_error =
#         pass

#     _, tmpl_rfn, ui_texts = ups_handler(0, error)
#     tmpl = render_ template(tmpl_rfn, **ui_texts)
#     return tmpl


def create_ups_tmpl(error: str, code: int = 0):
    _, tmpl_rfn, ui_texts = ups_handler(code, error)
    tmpl = process_template(tmpl_rfn, **ui_texts)
    return tmpl


def uiact_response(code: str) -> Tuple[jinja_template, UiActResponse]: #| None]: Too many warns with None
    """
    This func decodes a uiact response
    """

    error_tmpl = ''
    uiact_rsp = None
    try:
        rqs_method = get_method()

        def _get_error(param: str) -> str:
            return f"Unexpected uiact route parameter [{param}]."

        def _get_result() -> Tuple[jinja_template, UiActResponse | None]:
            uiact_rsp = None
            error_tmpl: jinja_template = ''
            cmd_text: json_txt = request.args.get(js_form_cargo_id, '') if rqs_method == MTD_GET else request.form.get(js_form_cargo_id, '')
            if is_str_none_or_empty(cmd_text):
                error_tmpl = create_ups_tmpl( _get_error("empty") )
            elif not (uiact_rsp:= UiActResponse(cmd_text)):
                error_tmpl = create_ups_tmpl(_get_error("none"))
            elif is_str_none_or_empty(uiact_rsp.action):
                error_tmpl = create_ups_tmpl(_get_error("action: ''"))

            return error_tmpl, uiact_rsp

        if rqs_method == MTD_POST and not is_str_none_or_empty(msg_error:= js_form_sec_check()):
            error_tmpl = create_ups_tmpl(msg_error)
        elif code == js_form_cargo_id:
            # the code is send via a html form's input or on the parameter
            error_tmpl, uiact_rsp = _get_result()
        elif not is_str_none_or_empty(code):
            uiact_rsp = UiActResponse(code)
        else:
            error_tmpl, uiact_rsp = _get_result()

    except Exception as e:
        uiact_rsp = None
        _, tmpl_rfn, ui_texts = ups_handler(0, str(e), e)
        error_tmpl = process_template(tmpl_rfn, **ui_texts)

    return error_tmpl, uiact_rsp


def grid_route(code: str, editor: str, show_grid: Callable) -> jinja_template:
    """
    This func routes calls from a grid or to a grid. 8—|
    see sep_grid & scm_grid
    """

    if nobody_is_logged():
        return redirect_to(login_route())

    go_tmpl: jinja_template = ''
    tmpl, uiact_rsp = uiact_response(code)

    if tmpl:
        go_tmpl= tmpl
    elif uiact_rsp and uiact_rsp.code == UiActResponseProxy.show:
        go_tmpl= show_grid()
    elif uiact_rsp:
        def _goto(item_code: str) -> str:
            url = private_route(editor, code=item_code)
            return redirect_to(url)

        match uiact_rsp.action:
            case UiActResponseKeys.insert:
                go_tmpl = _goto(UiActResponseProxy.add)
            case UiActResponseKeys.edit:
                data = uiact_rsp.encode()
                go_tmpl = _goto(data)
            case UiActResponseKeys.delete:
                go_tmpl = create_ups_tmpl("The Delete procedure is still under development.")
            case _:
                go_tmpl = create_ups_tmpl(f"Unknown route action '{uiact_rsp.action}'.")

    return go_tmpl

@login_required
@bp_private.route("/sep_grid/<code>", methods=MTD_ANY)
def sep_grid(code: str = "?"):
    """
    Through this route, the admin user can CRUD seps and display a grid
    """
    from .sep_grid import get_sep_grid

    error_tmpl, uiact_rsp = uiact_response(code)
    if not is_str_none_or_empty(error_tmpl):
        return error_tmpl
    elif uiact_rsp.code == UiActResponseProxy.show:
        return get_sep_grid()
    else:
        url = private_route("sep_edit", code=uiact_rsp.code)
        return redirect_to(url)


@login_required
@bp_private.route("/sep_edit/<code>", methods=MTD_ANY)
def sep_edit(code: str = "?"):
    """
    Through this route, the user can edit a SEP
    """

    if nobody_is_logged():
        return redirect_to(login_route())

    from .sep_new_edit import do_sep_edit

    return do_sep_edit(code)


@login_required
@bp_private.route("/scm_export/<code>", methods=MTD_ANY)
def scm_export(code: str = "?"):
    """
    Through this route, the user gets the export UI
    Where the SEP arrangement can be edited and/or DB exported
    """
    if nobody_is_logged():
        return redirect_to(login_route())

    error_tmpl, uiact_rsp = uiact_response(code)
    if not is_str_none_or_empty(error_tmpl):
        return error_tmpl
    elif uiact_rsp.code == UiActResponseProxy.show:
        from .scm_export_ui import scm_export_ui
        return scm_export_ui(uiact_rsp)
    elif uiact_rsp.action == UiActResponseKeys.export:
        from .scm_export_db import scm_export_db
        return scm_export_db(uiact_rsp)
    elif uiact_rsp.action == UiActResponseKeys.save:
        from .scm_export_layout import scm_export_layout
        return scm_export_layout(uiact_rsp)

    return redirect_to(login_route())



@login_required
@bp_private.route("/scm_grid/<code>", methods=MTD_ANY)
def scm_grid(code: str = "?"):
    """
    Through this route, the user can edit and insert a Schema
    """
    from .scm_grid import get_scm_grid

    return grid_route(code, "scm_edit", get_scm_grid)


@login_required
@bp_private.route("/scm_edit/<code>", methods=MTD_ANY)
def scm_edit(code: str = "?"):
    """
    Through this route, the user can edit a Schema
    """

    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .scm_new_edit import do_scm_edit

        return do_scm_edit(code)


@login_required
@bp_private.route("/receive_file", methods=MTD_ANY)
def receive_file():
    """
    Through this route, the user sends a zip file or a URL link for validation.

    If it passes the simple validations confronted in receive_file.py,
    it is unzipped and sent to data_validate
    (see module `data_validate`).
    The report generated by `data_validate` is sent by e-mail and
    a result message is displayed to the user.

    Part of Canoa `Data Validation` Processes
    """

    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .receive_file import receive_file

        html = receive_file()
        return html

# DIDN'T FIND WERE IS CALLED
#===========================
# @login_required
# @bp_private.route("/received_files_get", methods=[MTD_POST])
# def received_files_get() -> str:
#     """
#     Through this route, the user obtains a list of the files
#     received so that they can examine them and download them.
#     """
#     if nobody_is_logged():
#         return redirect_to(login_route())
#     else:
#         from .received_files.fetch_records import fetch_record_s

#         records, _, _ = fetch_record_s('')
#         json = records.to_json()

#         return json


@login_required
@bp_private.route("/received_files_mgmt", methods=MTD_ANY)
def received_files_mgmt():
    """
    Through this route, the user gets a grid that allows
    him to manage and download the files he has sent for
    validation.

    When the user is power_user, he can request files from an other user_id
    """

    if nobody_is_logged():
        return redirect_to(login_route())
    elif not is_method_get():
        return redirect_to(login_route())
    else:
        rid = request.args.get("id", type=int)  # Get 'id' from Request
        id = current_user.id if rid is None else rid
        from .received_files.init_grid import init_grid

        html = init_grid(id)

        return html


@login_required
@bp_private.route("/received_file_download", methods=[MTD_POST])
def received_file_download():
    """
    Through this route, the user request to download one of the files
    he has send for validation or it's generated report.
    """
    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .received_files.download_record import download_rec

        html = download_rec()
        return html


@login_required
@bp_private.route("/change_password", methods=MTD_ANY)
def change_password():
    """
    'change_password page, as it's name
    implies, allows the user to change
    is password, for what ever reason
    at all or none.
    Whew! That's four lines :--)
    """

    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .access_control.password_change import do_password_change

        return do_password_change()


@bp_private.route("/logout")
def logout():
    """
    Logout the current user
    and the page is redirect to
    login
    """
    internal_logout()
    return redirect_to(login_route())


# eof
