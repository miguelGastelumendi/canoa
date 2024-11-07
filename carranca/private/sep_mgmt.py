"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

import json
from typing import Any, List, Tuple
from flask import render_template, request

from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.user_helper import get_batch_code
from ..helpers.route_helper import get_private_form_data


def do_sep_mgmt() -> str:
    from .models import MgmtUserSep

    task_code = 0
    template, is_get, texts = get_private_form_data("sepMgmt")
    js_grid_sec_value = "7298kaj0fk9dl-sd=)0x"
    js_grid_sec_key = "gridSecKey"
    js_grid_rsp = "gridRsp"
    js_grid_submit_id = "gridSubmitID"

    # Até criar ui_texts:
    texts["itemNone"] = "(nenhum)"
    texts["itemRemove"] = "(remover)"
    # py/js communication
    texts[js_grid_rsp] = js_grid_rsp
    texts["gridSecValue"] = js_grid_sec_value
    texts[js_grid_submit_id] = js_grid_submit_id
    texts[js_grid_sec_key] = js_grid_sec_key

    def __get_grid_data():
        users_sep, sep_list, msg_error = MgmtUserSep.get_grid_view(texts["itemNone"])
        sep_name_list = [sep["name"] for sep in sep_list]
        return users_sep, sep_name_list, msg_error

    if is_get:
        users_sep, sep_name_list, msg_error = __get_grid_data()
        texts["msgInfo"] = (
            """
            Para atribuir um SEP, selecione um da lista 'Novo SEP'.
            Use o item (Remover) para cancelar a atribuição.
            Para criar um novo SEP, use o botão [Adicionar] e [Editar] para alterá-lo.
            """
        )
    elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
        texts["msgError"] = "A chave mudou."
        # TODO goto login
    else:
        task_code += 1
        txtGridResponse = request.form.get(js_grid_rsp)
        task_code += 1
        jsonGridResponse = json.loads(txtGridResponse)
        task_code += 1
        batch_code = get_batch_code()
        # save data to db
        msg_success, msg_error_save, task_code = _save_data(jsonGridResponse, batch_code, task_code)
        task_code += 1
        if is_str_none_or_empty(msg_error_save):  # send mails
            msg_error_mail, task_code = _send_email(batch_code, task_code)
            msg_email = (
                "Os emails foram enviados."
                if is_str_none_or_empty(msg_error_mail)
                else "mais houve um error ao enviar os emails [{0}].".format(msg_error_mail)
            )
            msg_success = f"{msg_success} {msg_email}"

        users_sep, sep_name_list, msg_error_read = __get_grid_data()
        if is_str_none_or_empty(msg_error_save) and is_str_none_or_empty(msg_error_read):
            texts["msgSuccess"] = msg_success
        elif is_str_none_or_empty(msg_error_save):
            texts["msgError"] = msg_error_read
        else:
            texts["msgError"] = msg_error_save

    tmpl = render_template(template, usersSep=users_sep, sepList=sep_name_list, **texts)
    return tmpl


def _save_data(grid_response: dict, batch_code: str, task_code: int) -> Tuple[str, str]:
    """saves user modifications to the DB via the view's trigger"""
    task_code += 1
    msg_success = "As modificações foram salvas."
    msg_error = ""
    try:
        actions = grid_response["actions"]
        task_code += 1
        str_remove = actions["remove"]
        task_code += 1
        str_none = actions["none"]
        task_code += 1
        remove = []
        assign = []
        none = 0
        grid = grid_response["grid"]
        task_code += 1
        for item in grid:
            sep_new = item["sep_new"]
            if sep_new == str_none:
                none += 1
            elif sep_new != str_remove:  # new sep
                assign.append(item)
            elif item["sep_name"] != str_none:  # ignore remove none
                remove.append(item)

        if len(remove) + len(assign) == 0:
            return "Nenhuma tarefa a ser feita.", "", task_code

        task_code += 1
        msg_error = _save_grid_view(remove, assign, batch_code)
        if is_str_none_or_empty(msg_error):
            msg_success = f"{0} remoções e {1} atribuições foram realizadas.".format(
                len(remove), len(assign)
            )
    except Exception as e:
        msg_error = str(e)

    return msg_success, msg_error, task_code


def _save_grid_view(remove_list: List[Any], update_list: List[Any], batch_code: str) -> str:
    """
    Saves user-made changes to the UI grid to the database
    via an 'instead-of' trigger that:
        1) updates `users`;
        2) inserts new SEPs into the `sep` table (if any), and
        3) logs the changes to the `log_user_sep` log.
    """
    from flask_login import current_user
    from carranca import Session
    from .models import MgmtUserSep
    from ..Sidekick import sidekick

    remove_count = len(remove_list)
    update_count = len(update_list)

    if (remove_count + update_count) == 0:
        return None

    msg_error = None
    assigned_by = current_user.id
    user_not_found = []
    session = Session()
    try:

        def __set_user_sep_new(id: int, sep_new: str):
            user_sep = session.query(MgmtUserSep).filter_by(user_id=id).one_or_none()
            if user_sep:
                user_sep.sep_new = sep_new
                user_sep.assigned_by = assigned_by
                user_sep.batch_code = batch_code
            else:
                sidekick.app_log.error(f"{__name__}: User with ID {id} not found, cannot update.")
                user_not_found.append(id)

        id = "user_id"
        # TODO auto remove reassignment
        for user_sep_data in remove_list:  # first remove
            __set_user_sep_new(user_sep_data[id], None)

        for user_sep_data in update_list:  # then update
            __set_user_sep_new(user_sep_data[id], user_sep_data["sep_new"])

        session.commit()
    except Exception as e:
        session.rollback()
        msg_error = f"Unable to commit data: [{str(e)}]."
        sidekick.app_log.error(msg_error)
    finally:
        session.close()

    return msg_error


def _send_email(batch_code: str, task_code: int) -> Tuple[str, str]:
    """
    Send an email for each user with a
    'new' SEP or if it was removed
    """
    from carranca import Session
    from .models import MgmtEmailSep
    from ..Sidekick import sidekick
    from ..helpers.py_helper import now

    task_code += 1
    msg_error = None
    session = Session()
    try:
        user_emails = session.query(MgmtEmailSep).filter_by(batch_code=batch_code).all()
        if not user_emails:
            return None
        for user in user_emails:
            user.email_at = now()
            user.email_error = None

        session.commit()

    # session.commit()
    except Exception as e:
        session.rollback()
        msg_error = f"Unable to read email data: [{str(e)}]."
        sidekick.app_log.error(msg_error)
    finally:
        session.close()

    return msg_error, task_code


# eof
