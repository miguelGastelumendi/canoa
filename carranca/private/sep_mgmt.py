"""
    User Profile's Management and SEP assignment

    Equipe da Canoa -- 2024
    mgd 2024-10-09
"""

# cSpell: ignore mgmt tmpl

import json
from typing import Tuple
from flask import render_template, request

from .models import MgmtUserSep, SepRecords
from ..Sidekick import sidekick
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.user_helper import get_batch_code
from ..helpers.error_helper import ModuleErrorCode
from ..helpers.route_helper import get_private_form_data
from ..helpers.hints_helper import TextsUI


proc_return = Tuple[str, str, int]


def do_sep_mgmt() -> str:

    task_code = 0  # ModuleErrorCode.SEP_MANAGEMENT.value
    try:
        task_code += 1
        template, is_get, uiTexts = get_private_form_data("sepMgmt")

        js_grid_sec_value = "7298kaj0fk9dl-sd=)0x"
        js_grid_sec_key = "gridSecKey"
        js_grid_rsp = "gridRsp"
        js_grid_submit_id = "gridSubmitID"

        # Até criar ui_texts:
        uiTexts["itemNone"] = "(nenhum)"
        uiTexts["itemRemove"] = "(remover)"
        # py/js communication
        uiTexts[js_grid_rsp] = js_grid_rsp
        uiTexts["gridSecValue"] = js_grid_sec_value
        uiTexts[js_grid_submit_id] = js_grid_submit_id
        uiTexts[js_grid_sec_key] = js_grid_sec_key

        def __get_grid_data():
            users_sep, sep_list, msg_error = MgmtUserSep.get_grid_view(uiTexts["itemNone"])
            sep_name_list = [sep["name"] for sep in sep_list]
            return users_sep, sep_name_list, msg_error

        if is_get:
            users_sep, sep_name_list, msg_error = __get_grid_data()
            if not is_str_none_or_empty(msg_error):
                uiTexts["msgError"] = msg_error
            else:
                uiTexts["msgInfo"] = (
                    """
                    Para atribuir um SEP, selecione um da lista 'Novo SEP'.
                    Use o item (Remover) para cancelar a atribuição.
                    Para criar um novo SEP, use o botão [Adicionar] e [Editar] para alterá-lo.
                    """
                )
        elif request.form.get(js_grid_sec_key) != js_grid_sec_value:
            uiTexts["msgError"] = "A chave mudou."
            # TODO goto login
        else:
            task_code += 1
            txtGridResponse = request.form.get(js_grid_rsp)
            msg_success, msg_error, task_code = _save_and_email(txtGridResponse, uiTexts, task_code)
            task_code += 1
            users_sep, sep_name_list, msg_error_read = __get_grid_data()
            if is_str_none_or_empty(msg_error) and is_str_none_or_empty(msg_error_read):
                uiTexts["msgSuccess"] = msg_success
            elif is_str_none_or_empty(msg_error):
                uiTexts["msgError"] = msg_error_read
            else:
                uiTexts["msgError"] = msg_error

    except Exception as e:
        # msg = add_msg_error("errorPasswordChange", uiTexts, task_code)
        sidekick.app_log.error(e)

    tmpl = render_template(template, usersSep=users_sep, sepList=sep_name_list, **uiTexts)
    return tmpl


def _save_and_email(txtGridResponse: str, uiTexts: TextsUI, task_code: int) -> proc_return:
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
    grid_response: dict[str, any], batch_code: str, uiTexts: TextsUI, task_code: int
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
            return "Nenhuma tarefa a ser feita.", "", task_code

        task_code += 1
        _, msg_error, task_code = _save_data_to_db(remove, assign, batch_code, uiTexts, task_code)
        task_code += 1
        if is_str_none_or_empty(msg_error):
            msg_success = f"{0} remoções e {1} atribuições foram realizadas.".format(
                len(remove), len(assign)
            )
    except Exception as e:
        msg_error = f"Unable to prepare/send data {task_code}: [{str(e)}]."

    return msg_success, msg_error, task_code


def _prepare_data_to_save(
    grid_response: dict[str, any], uiTexts: TextsUI, task_code: int
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
            sep_new = item["sep_new"]
            if sep_new == str_none:
                pass
            elif sep_new != str_remove:  # new sep
                assign.append(item)
            elif item["sep_name"] != str_none:  # ignore remove none
                remove.append(item)

    except Exception as e:
        # uiTexts:
        msg_error = f"Unable to prepare data {task_code}: [{str(e)}]."

    return msg_error, remove, assign, task_code


def _save_data_to_db(
    remove: SepRecords, update: SepRecords, batch_code: str, uiTexts: TextsUI, task_code: int
) -> proc_return:
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

    msg_error = None
    assigned_by = current_user.id
    user_not_found = []
    task_code += 1
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
        task_code += 1
        for user_sep_data in remove:  # first remove
            __set_user_sep_new(user_sep_data[id], None)

        task_code += 1
        for user_sep_data in update:  # then update
            __set_user_sep_new(user_sep_data[id], user_sep_data["sep_new"])

        task_code += 1
        session.commit()
    except Exception as e:
        session.rollback()
        # uiTexts:
        msg_error = f"Unable to commit data {task_code}: [{str(e)}]."
        sidekick.app_log.error(msg_error)
    finally:
        session.close()

    return "", msg_error, task_code


def _send_email(batch_code: str, uiTexts: TextsUI, task_code: int) -> proc_return:
    """
    Send an email for each user with a
    'new' SEP or if it was removed
    """
    from carranca import Session
    from .models import MgmtEmailSep
    from ..Sidekick import sidekick
    from ..helpers.py_helper import now
    from ..helpers.email_helper import send_email

    task_code += 1
    msg_error = None
    session = Session()
    try:
        user_emails = session.query(MgmtEmailSep).filter_by(batch_code=batch_code).all()
        if not user_emails:
            return None, "Nenhum e-mail pendente encontrado", task_code

        email_send = 0
        email_error = 0
        invalid_state = []
        texts = {}
        texts["subject"] = "Novidades sobre o seu SEP em Canoa"
        intro = "Prezado {0},<br>"
        uiTexts["sepSetNew"] = (
            "Prezado {0},<br><br>Nesta data, o SEP '{1}' foi atribuído para você.<br><br><i>Equipe Canoa</i>"
        )
        uiTexts["sepRemoved"] = (
            "Prezado {0},<br><br>A partir desta data, o SEP '{2}' não estará mais a seu cuidado.<br><br><i>Equipe Canoa</i>"
        )
        uiTexts["sepChanged"] = (
            "Prezado {0},<br><br>A partir desta data, O SEP '{1}' estará sob seus cuidados no lugar do SEP '{2}'.<br><br><i>Equipe Canoa</i>"
        )
        for user in user_emails:
            msg = None
            try:
                if user.sep_name_old == None and user.sep_name_new == None:
                    invalid_state.append(user)
                elif user.sep_name_old == None:
                    msg = uiTexts["sepSetNew"].format(user.user_name, user.sep_name_new)
                elif user.sep_name_new == None:
                    msg = uiTexts["sepRemoved"].format(user.user_name, user.sep_name_new, user.sep_name_old)
                else:
                    msg = uiTexts["sepChanged"].format(user.user_name, user.sep_name_new, user.sep_name_old)

                texts["content"] = msg
                if send_email(user.user_email, texts):
                    user.email_at = now()
                    email_send += 1
                else:
                    raise Exception("email was not send, no error was generated.")
            except Exception as e:
                user.email_error = str(e)
                email_error += 1

        session.commit()

    # session.commit()
    except Exception as e:
        session.rollback()
        msg_error = f"Unable to send email {task_code}: [{str(e)}]."
        sidekick.app_log.error(msg_error)
    finally:
        session.close()

    return "Emails enviados com sucesso.", msg_error, task_code


# eof
