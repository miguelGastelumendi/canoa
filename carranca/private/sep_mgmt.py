"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl samp

import json
from typing import Tuple
from flask import render_template, request

from ..helpers.pw_helper import internal_logout

from .models import MgmtUserSep, SepRecords
from .SepIconConfig import SepIconConfig

from ..Sidekick import sidekick
from ..helpers.db_helper import try_get_mgd_msg
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.user_helper import get_batch_code
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data, init_form_vars
from ..helpers.hints_helper import UI_Texts
from ..helpers.ui_texts_helper import (
    add_msg_fatal,
    format_ui_item,
    ui_DialogIcon,
    ui_msg_error,
    ui_msg_success,
    ui_msg_exception,
)

proc_return = Tuple[str, str, int]


def do_sep_mgmt() -> str:

    task_code = ModuleErrorCode.SEP_MANAGEMENT.value
    _, template, is_get, uiTexts = init_form_vars()

    users_sep = []
    sep_fullname_list = []

    try:
        task_code += 1  # 1
        template, is_get, uiTexts = get_private_form_data("sepMgmt")

        task_code += 1  # 2
        # TODO: create a real key with user_id and datetime
        js_grid_sec_value = "7298kaj0fk9dl-sd=)0x"
        # uiTexts keys used in JavaScript
        js_grid_sec_key = "gridSecKey"
        js_grid_rsp = "gridRsp"
        js_grid_submit_id = "gridSubmitID"

        # py/js communication
        uiTexts[js_grid_rsp] = js_grid_rsp
        uiTexts["gridSecValue"] = js_grid_sec_value
        uiTexts[js_grid_submit_id] = js_grid_submit_id
        uiTexts[js_grid_sec_key] = js_grid_sec_key

        uiTexts[ui_DialogIcon] = SepIconConfig.set_url(SepIconConfig.none_file)

        task_code += 1  # 3
        colData = json.loads(uiTexts["colData"])
        task_code += 1  # 4
        # grid columns, colData & colNames *must* match
        colNames = ["user_id", "file_url", "user_name", "scm_sep_curr", "scm_sep_new", "when"]
        task_code += 1  # 5
        # Rewrite it in an easier way to express it in js: colName: colHeader
        uiTexts["colData"] = [{"n": key, "h": colData[key]} for key in colNames]

        def __get_grid_data():
            users_sep, sep_list, msg_error = MgmtUserSep.get_grid_view(uiTexts["itemNone"])
            sep_fullname_list = [sep["fullname"] for sep in sep_list]
            return users_sep, sep_fullname_list, msg_error

        if is_get:
            task_code += 1  # 6
            users_sep, sep_fullname_list, uiTexts[ui_msg_error] = __get_grid_data()
        elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
            task_code += 2  # 7
            uiTexts[ui_msg_exception] = uiTexts["secKeyViolation"]
            internal_logout()
        else:
            task_code += 3
            txtGridResponse = request.form.get(js_grid_rsp)
            msg_success, msg_error, task_code = _save_and_email(txtGridResponse, uiTexts, task_code)
            task_code += 1
            users_sep, sep_fullname_list, msg_error_read = __get_grid_data()
            if is_str_none_or_empty(msg_error) and is_str_none_or_empty(msg_error_read):
                uiTexts[ui_msg_success] = msg_success
            elif is_str_none_or_empty(msg_error):
                uiTexts[ui_msg_error] = msg_error_read
            else:
                uiTexts[ui_msg_error] = msg_error

    except Exception as e:
        msg = add_msg_fatal("gridException", uiTexts, task_code)
        sidekick.app_log.error(e)
        sidekick.display.error(msg)
        # Todo error with users_sep,,, not ready

    tmpl = render_template(template, usersSep=users_sep, sepList=sep_fullname_list, **uiTexts)
    return tmpl


def _save_and_email(txtGridResponse: str, uiTexts: UI_Texts, task_code: int) -> proc_return:
    """Saves data & sends emails"""
    task_code += 1
    jsonGridResponse = json.loads(txtGridResponse)
    task_code += 1
    batch_code = get_batch_code()
    msg_success_save, msg_error, task_code = _save_data(jsonGridResponse, batch_code, uiTexts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    task_code += 1
    msg_success_email, msg_error, task_code = _send_email(batch_code, uiTexts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    msg_success = f"{msg_success_save} {msg_success_email}"
    return msg_success, None, task_code


def _save_data(
    grid_response: dict[str, any], batch_code: str, uiTexts: UI_Texts, task_code: int
) -> proc_return:
    """saves user modifications to the DB via the view's trigger"""
    msg_success = None
    msg_error = None
    try:
        msg_error, remove, assign, task_code = _prepare_data_to_save(grid_response, uiTexts, task_code)
        task_code += 1
        if not is_str_none_or_empty(msg_error):
            return "", msg_error, task_code
        elif len(remove) + len(assign) == 0:
            return uiTexts["tasksNothing"], "", task_code

        task_code += 1
        _, msg_error, task_code = _save_data_to_db(remove, assign, batch_code, uiTexts, task_code)
        task_code += 1
        if is_str_none_or_empty(msg_error):
            msg_success = format_ui_item(uiTexts, "tasksSuccess", len(remove), len(assign))
    except Exception as e:
        msg_error = format_ui_item(uiTexts, "tasksError", task_code, str(e))

    return msg_success, msg_error, task_code


def _prepare_data_to_save(
    grid_response: dict[str, any], uiTexts: UI_Texts, task_code: int
) -> Tuple[str, SepRecords, SepRecords, int]:
    """Distributes the modifications in two groups: remove & assign"""

    msg_error = None
    try:
        actions = grid_response["actions"]
        task_code += 1
        str_remove: str = actions["remove"]
        task_code += 1
        str_none: str = actions["none"]
        task_code += 1
        remove: SepRecords = []
        assign: SepRecords = []
        grid: SepRecords = grid_response["grid"]
        task_code += 1
        for item in grid:
            sep_new = item["scm_sep_new"]
            if sep_new == str_none:
                pass
            elif sep_new != str_remove:  # new sep
                assign.append(item)
            elif item["scm_sep_curr"] != str_none:  # ignore remove none
                remove.append(item)

    except Exception as e:
        # uiTexts:
        msg_error = format_ui_item(uiTexts, "taskPrepare", task_code, str(e))

    return msg_error, remove, assign, task_code


def _save_data_to_db(
    remove: SepRecords, update: SepRecords, batch_code: str, uiTexts: UI_Texts, task_code: int
) -> proc_return:
    """
    Saves user-made changes to the UI grid to the database
    via an 'instead-of' trigger that:
        1) updates `users`;
        2) inserts new SEPs into the `sep` table (if any), and
        3) logs the changes to the `log_user_sep` log.
    """

    from carranca import SqlAlchemySession
    from .models import MgmtUserSep
    from .logged_user import logged_user
    from ..Sidekick import sidekick

    msg_error = None
    assigned_by = logged_user.id
    user_not_found = []
    task_code += 1
    with SqlAlchemySession() as db_session:
        try:

            def __set_user_sep_new(id: int, sep_new: str):
                user_sep = db_session.query(MgmtUserSep).filter_by(user_id=id).one_or_none()
                if user_sep:
                    user_sep.scm_sep_new = sep_new
                    user_sep.assigned_by = assigned_by
                    user_sep.batch_code = batch_code
                else:
                    sidekick.app_log.error(f"{__name__}: User with ID {id} not found, cannot update.")
                    user_not_found.append(id)

            id = "user_id"
            # TODO auto remove reassignment
            task_code += 1
            for user_sep_data in remove:  # first remove
                __set_user_sep_new(user_sep_data[id], None)

            task_code += 1
            for user_sep_data in update:  # then update
                __set_user_sep_new(user_sep_data[id], user_sep_data["scm_sep_new"])

            task_code += 1
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            # uiTexts:
            msg_error = try_get_mgd_msg(e, f"Unable to commit data {task_code}: [{e}].")
            sidekick.app_log.error(msg_error)

    return "", msg_error, task_code


def _send_email(batch_code: str, uiTexts: UI_Texts, task_code: int) -> proc_return:
    """
    Send an email for each user with a
    'new' SEP or if it was removed
    """
    from carranca import SqlAlchemySession
    from .models import MgmtEmailSep
    from ..Sidekick import sidekick
    from ..helpers.py_helper import now
    from ..helpers.email_helper import send_email

    task_code += 1
    msg_error = None
    with SqlAlchemySession() as db_session:
        try:
            user_emails = db_session.query(MgmtEmailSep).filter_by(batch_code=batch_code).all()
            if not user_emails:
                return None, uiTexts["emailNone"], task_code

            email_send = 0
            email_error = 0
            invalid_state = []
            texts = {}
            texts["subject"] = uiTexts["emailSubject"]
            for user in user_emails:
                msg = None
                try:
                    if user.sep_name_old == None and user.sep_name_new == None:
                        invalid_state.append(user)
                    elif user.sep_name_old == None:
                        msg = format_ui_item(uiTexts, "emailSetNew", user.user_name, user.sep_name_new)
                    elif user.sep_name_new == None:
                        msg = format_ui_item(
                            uiTexts, "emailRemoved", user.user_name, user.sep_name_new, user.sep_name_old
                        )
                    else:
                        msg = format_ui_item(
                            uiTexts, "emailChanged", user.user_name, user.sep_name_new, user.sep_name_old
                        )

                    texts["content"] = msg
                    if send_email(user.user_email, texts):
                        user.email_at = now()
                        email_send += 1
                    else:
                        raise Exception(uiTexts["emailError"])
                except Exception as e:
                    user.email_error = str(e)
                    email_error += 1

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            msg_error = format_ui_item(uiTexts, "emailException", task_code, str(e))
            sidekick.app_log.error(msg_error)

    return uiTexts["emailSuccess"], msg_error, task_code


# eof
