"""
User Profile's Management and SEP assignment

NB: SEP is an old acronym for
    "Setor Estratégico de Planejamento" (Strategic Planning Sector)
    so it was kept here

Equipe da Canoa -- 2024
mgd 2024-10-09, 2025-01-09

"""

# cSpell: ignore mgmt tmpl samp

import json
from flask import render_template, request
from typing import TypeAlias, Tuple, List
from sqlalchemy.orm import Session

from .models import MgmtUserSep_
from .SepIconConfig import SepIconConfig
from .sep_icon import icon_prepare_for_html

from ..public.ups_handler import ups_handler
from ..common.app_error_assistant import ModuleErrorCode

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.db_helper import DBRecords, ListOfDBRecords, try_get_mgd_msg
from ..helpers.user_helper import get_batch_code
from ..helpers.js_grid_helper import js_grid_constants, js_grid_sec_key, js_grid_rsp, js_grid_sec_value
from ..helpers.email_helper import RecipientsListStr
from ..helpers.route_helper import get_private_form_data, init_form_vars
from ..helpers.types_helper import ui_db_texts
from ..helpers.ui_db_texts_helper import (
    add_msg_fatal,
    format_ui_item,
    UITextsKeys,
)

# def returns
def_return: TypeAlias = Tuple[str, str, int]


def sep_data_fetch(_item_none) -> Tuple[DBRecords, List[str], str]:

    users_sep, sep_list, msg_error = MgmtUserSep_.get_grid_view()
    for record in users_sep.records:
        record.scm_sep_new = _item_none
        record.scm_sep_curr = _item_none if record.scm_sep_curr is None else record.scm_sep_curr
        record.file_url = icon_prepare_for_html(record.sep_id)[0]  # url

    sep_fullname_list = [sep.sep_fullname for sep in sep_list.records]

    return users_sep, sep_fullname_list, msg_error


def do_sep_mgmt() -> str:
    task_code = ModuleErrorCode.SEP_MGMT.value
    _, template, is_get, ui_texts = init_form_vars()

    users_sep: ListOfDBRecords = []
    sep_fullname_list = []
    msg_error: str = None
    tmpl = ""
    try:
        task_code += 1  # 1
        template, is_get, ui_texts = get_private_form_data("sepMgmt_v1")

        task_code += 1  # 2
        ui_texts[UITextsKeys.Form.icon] = SepIconConfig.set_url(SepIconConfig.none_file)

        task_code += 1  # 3
        col_names = ["user_id", "file_url", "user_name", "scm_sep_curr", "scm_sep_new", "when"]
        grid_const, _ = js_grid_constants(ui_texts["colMetaInfo"], col_names)
        users_sep = []
        item_none = "(None)" if is_str_none_or_empty(ui_texts["itemNone"]) else ui_texts["itemNone"]
        if is_get:
            task_code += 1  # 6
            users_sep, sep_fullname_list, ui_texts[UITextsKeys.Msg.error] = sep_data_fetch(item_none)
        elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
            # TODO: up_handler
            task_code += 2  # 7
            ui_texts[UITextsKeys.Msg.exception] = ui_texts["secKeyViolation"]
            # TODO internal_logout()
        else:
            task_code += 3
            txtGridResponse = request.form.get(js_grid_rsp)
            msg_success, msg_error, task_code = _save_and_email(txtGridResponse, ui_texts, task_code)
            task_code += 1
            _, _, users_sep, sep_fullname_list, msg_error_read = sep_data_fetch(item_none)
            if is_str_none_or_empty(msg_error) and is_str_none_or_empty(msg_error_read):
                ui_texts[UITextsKeys.Msg.success] = msg_success
            elif is_str_none_or_empty(msg_error):
                ui_texts[UITextsKeys.Msg.error] = msg_error_read
            else:
                ui_texts[UITextsKeys.Msg.error] = try_get_mgd_msg(
                    msg_error, ui_texts["saveError"].format(task_code)
                )

        tmpl = render_template(
            template,
            usersSep=users_sep.to_json(),
            sepList=sep_fullname_list,
            **grid_const,
            **ui_texts,
        )

    except Exception as e:
        msg = add_msg_fatal("gridException", ui_texts, task_code)
        _, template, ui_texts = ups_handler(task_code, msg, e, False)
        tmpl = render_template(template, **ui_texts)

    return tmpl


def _save_and_email(txtGridResponse: str, ui_texts: ui_db_texts, task_code: int) -> def_return:
    """Saves data & sends emails"""
    task_code += 1
    jsonGridResponse = json.loads(txtGridResponse)
    task_code += 1
    batch_code = get_batch_code()
    msg_success_save, msg_error, task_code = _save_data(jsonGridResponse, batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    task_code += 1
    msg_success_email, msg_error, task_code = _send_email(batch_code, ui_texts, task_code)
    if not is_str_none_or_empty(msg_error):
        return None, msg_error, task_code

    msg_success = f"{msg_success_save} {msg_success_email}"
    return msg_success, None, task_code


def _save_data(
    grid_response: dict[str, any], batch_code: str, ui_texts: ui_db_texts, task_code: int
) -> def_return:
    """saves user modifications to the DB via the view's trigger"""
    msg_success = None
    msg_error = None
    try:
        msg_error, remove, assign, task_code = _prepare_data_to_save(grid_response, ui_texts, task_code)
        task_code += 1
        if not is_str_none_or_empty(msg_error):
            return "", msg_error, task_code
        elif len(remove) + len(assign) == 0:
            return ui_texts["tasksNothing"], "", task_code

        task_code += 1
        _, msg_error, task_code = _save_data_to_db(remove, assign, batch_code, ui_texts, task_code)
        task_code += 1
        if is_str_none_or_empty(msg_error):
            msg_success = format_ui_item(ui_texts, "tasksSuccess", len(remove), len(assign))
    except Exception as e:
        msg_error = format_ui_item(ui_texts, "tasksError", task_code, str(e))

    return msg_success, msg_error, task_code


def _prepare_data_to_save(
    grid_response: dict[str, any], ui_texts: ui_db_texts, task_code: int
) -> Tuple[str, ListOfDBRecords, ListOfDBRecords, int]:
    """Distributes the modifications in two groups: remove & assign"""

    msg_error = None
    try:
        actions = grid_response["actions"]
        task_code += 1
        str_remove: str = actions["remove"]
        task_code += 1
        str_none: str = actions["none"]
        task_code += 1
        remove: ListOfDBRecords = []
        assign: ListOfDBRecords = []
        grid: ListOfDBRecords = grid_response["grid"]
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
        # ui_texts:
        msg_error = format_ui_item(ui_texts, "taskPrepare", task_code, str(e))

    return msg_error, remove, assign, task_code


def _save_data_to_db(
    remove: ListOfDBRecords, update: ListOfDBRecords, batch_code: str, ui_texts: ui_db_texts, task_code: int
) -> def_return:
    """
    Saves user-made changes to the UI grid to the database
    via an 'instead-of' trigger that:
        1) updates `users`;
        2) inserts new SEPs into the `sep` table (if any), and
        3) logs the changes to the `log_user_sep` log.
    """

    from carranca import global_sqlalchemy_scoped_session
    from .models import MgmtUserSep_

    from ..common.app_context_vars import logged_user, sidekick

    msg_error = None
    assigned_by = logged_user.id
    user_not_found = []
    task_code += 1
    db_session: Session
    with global_sqlalchemy_scoped_session() as db_session:
        try:

            def __set_user_sep_new(id: int, sep_new: str):
                user_sep = db_session.query(MgmtUserSep_).filter_by(user_id=id).one_or_none()
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
            # ui_texts:
            msg_error = try_get_mgd_msg(e, f"Unable to commit data {task_code}: [{e}].")
            sidekick.app_log.error(msg_error)

    return "", msg_error, task_code


def _send_email(batch_code: str, ui_texts: ui_db_texts, task_code: int) -> def_return:
    """
    Send an email for each user with a
    'new' SEP or if it was removed
    """
    from carranca import global_sqlalchemy_scoped_session
    from .models import MgmtEmailSep
    from ..common.app_context_vars import sidekick
    from ..helpers.py_helper import now
    from ..helpers.sendgrid_helper import send_email

    task_code += 1
    msg_error = None
    db_session: Session
    with global_sqlalchemy_scoped_session() as db_session:
        try:
            # The users involved in the `batch_code` batch modification.
            user_list = db_session.query(MgmtEmailSep).filter_by(batch_code=batch_code).all()
            if not user_list:
                return None, ui_texts["emailNone"], task_code

            email_send = 0
            email_error = 0
            invalid_state = []
            texts = {}
            texts["subject"] = ui_texts["emailSubject"]
            for user in user_list:
                msg = None
                try:
                    if user.sep_name_old == None and user.sep_name_new == None:
                        invalid_state.append(user)
                    elif user.sep_name_old == None:
                        msg = format_ui_item(ui_texts, "emailSetNew", user.user_name, user.sep_name_new)
                    elif user.sep_name_new == None:
                        msg = format_ui_item(
                            ui_texts, "emailRemoved", user.user_name, user.sep_name_new, user.sep_name_old
                        )
                    else:
                        msg = format_ui_item(
                            ui_texts, "emailChanged", user.user_name, user.sep_name_new, user.sep_name_old
                        )

                    texts["content"] = msg
                    if send_email(RecipientsListStr(user.user_email, user.user_name), texts):
                        user.email_at = now()
                        email_send += 1
                    else:
                        raise Exception(ui_texts["emailError"])
                except Exception as e:
                    user.email_error = str(e)
                    email_error += 1

            db_session.commit()
        except Exception as e:
            db_session.rollback()
            msg_error = format_ui_item(ui_texts, "emailException", task_code, str(e))
            sidekick.app_log.error(msg_error)

    return ui_texts["emailSuccess"], msg_error, task_code


# eof
