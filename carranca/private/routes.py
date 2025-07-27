"""
*Routes*
Private Routes
This routes are private, users _must be_ logged

Equipe da Canoa -- 2024
mgd
"""

# cSpell: ignore werkzeug wtforms tmpl mgmt jscmd
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from typing import Callable

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.pw_helper import internal_logout, nobody_is_logged
from ..public.ups_handler import ups_handler
from ..helpers.js_grid_helper import js_grid_rsp
from ..helpers.route_helper import (
    bp_name,
    base_route_private,
    get_private_response_data,
    is_method_get,
    login_route,
    private_route,
    redirect_to,
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
    return render_template(template, **texts)


@login_required
@bp_private.route("/sep_mgmt", methods=["GET", "POST"])
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


def grid_route(code: str, editor: str, show_grid: Callable):
    """
    This func routes calls from a grid or to a grid. 8—|
    see sep_grid & scm_grid
    """

    from .grid_helper import GridAction, GridCargoKeys, GridResponse

    def _goto(item_code: str) -> str:
        url = private_route(editor, code=item_code)
        return redirect_to(url)

    def _get_route_error(param: str) -> str:
        return f"Unexpected route parameter [{param}]."

    error = _get_route_error("?")
    if nobody_is_logged():
        return redirect_to(login_route())
    elif not is_method_get():
        error = _get_route_error("post")
    elif code == GridAction.show:
        return show_grid()
    elif code != js_grid_rsp:
        error = _get_route_error(code)
    # TODO security key  elif is_str_none_or_empty(sec_key:= request.args.get('grid_sec_key', '')) or (sec_key != ):
    elif is_str_none_or_empty(cmd_text := request.args.get(js_grid_rsp, "")):
        error = _get_route_error("empty")
    else:
        error = _get_route_error("jscmd")
        grid_response = GridResponse(cmd_text)
        action = grid_response.action
        error = _get_route_error("action")
        match action:
            case GridCargoKeys.insert:
                return _goto(GridAction.add)
            case GridCargoKeys.edit:
                data = GridResponse.do_data()
                return _goto(data)
            case GridCargoKeys.delete:
                error = f"The Delete procedure is still under development."
                # TODO Remove all
                pass

    _, tmpl_ffn, ui_texts = ups_handler(0, error)
    tmpl = render_template(tmpl_ffn, **ui_texts)
    return tmpl


@login_required
@bp_private.route("/sep_grid/<code>", methods=["GET", "POST"])
def sep_grid(code: str = "?"):
    """
    Through this route, the admin user can CRUD seps and display a grid
    """
    from .sep_grid import get_sep_grid

    return grid_route(code, "sep_edit", get_sep_grid)

    # from .grid_helper import GridAction, GridCargoKeys, GridResponse

    # def _goto(code: str) -> str:
    #     url = private_route("sep_edit", code=code)
    #     return redirect_to(url)

    # def _get_route_error(param: str) -> str:
    #     return f"Unexpected route parameter [{param}]."

    # error = _get_route_error("?")
    # if nobody_is_logged():
    #     return redirect_to(login_route())
    # elif not is_method_get():
    #     error = _get_route_error("post")
    # elif code == GridAction.show:
    #     return get_sep_grid()
    # elif code != js_grid_rsp:
    #     error = _get_route_error(code)
    # # TODO security key  elif is_str_none_or_empty(sec_key:= request.args.get('grid_sec_key', '')) or (sec_key != ):
    # elif is_str_none_or_empty(cmd_text := request.args.get(js_grid_rsp, "")):
    #     error = _get_route_error("empty")
    # else:
    #     error = _get_route_error("jscmd")
    #     grid_response = GridResponse(cmd_text)
    #     action = grid_response.action
    #     error = _get_route_error("action")
    #     match action:
    #         case GridCargoKeys.insert:
    #             return _goto(GridAction.add)
    #         case GridCargoKeys.edit:
    #             data = GridResponse.do_data()
    #             return _goto(data)
    #         case GridCargoKeys.delete:
    #             error = f"The Delete procedure is still under development."
    #             # TODO Remove all
    #             pass

    # _, tmpl_ffn, ui_texts = ups_handler(0, error)
    # tmpl = render_template(tmpl_ffn, **ui_texts)
    # return tmpl


@login_required
@bp_private.route("/sep_edit/<code>", methods=["GET", "POST"])
def sep_edit(code: str = "?"):
    """
    Through this route, the user can edit a SEP
    """

    if nobody_is_logged():
        return redirect_to(login_route())

    else:
        from .sep_new_edit import do_sep_edit

        return do_sep_edit(code)


@login_required
@bp_private.route("/scm_grid/<code>", methods=["GET", "POST"])
def scm_grid(code: str = "?"):
    """
    Through this route, the user can edit and insert a Schema
    """
    from .scm_grid import get_scm_grid

    return grid_route(code, "scm_edit", get_scm_grid)


@login_required
@bp_private.route("/scm_edit/<code>", methods=["GET", "POST"])
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
@bp_private.route("/receive_file", methods=["GET", "POST"])
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


@login_required
@bp_private.route("/received_files_get", methods=["POST"])
def received_files_get() -> str:
    """
    Through this route, the user obtains a list of the files
    received so that they can examine them and download them.
    """
    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .received_files.fetch_records import fetch_record_s

        records, _ = fetch_record_s()
        json = records.to_json()

        return json


@login_required
@bp_private.route("/received_files_mgmt", methods=["GET", "POST"])
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
@bp_private.route("/received_file_download", methods=["POST"])
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
@bp_private.route("/change_password", methods=["GET", "POST"])
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
