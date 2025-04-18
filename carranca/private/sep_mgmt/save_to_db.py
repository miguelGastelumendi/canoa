"""
SEP Management and User assignment
Save data to the DB

Equipe da Canoa -- 2025
mgd 202-04-09
"""

# cSpell: ignore mgmt

from typing import Dict, Tuple

from sqlalchemy.orm import Session

from ...helpers.py_helper import is_str_none_or_empty
from ...helpers.db_helper import ListOfDBRecords, try_get_mgd_msg
from ...helpers.types_helper import ui_db_texts, sep_mgmt_rtn
from ...helpers.ui_db_texts_helper import format_ui_item

from .dict_keys import MgmtCol, CargoKeys


def save_data(
    grid_response: Dict[str, str],
    batch_code: str,
    ui_texts: ui_db_texts,
    task_code: int,
) -> sep_mgmt_rtn:  # msg_success, msg_error, task_code
    """Saves user modifications to the DB via the view's trigger"""

    msg_success = None
    msg_error = None
    try:
        msg_error, remove, assign, task_code = _prepare_data_to_save(grid_response, ui_texts, task_code)
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
    grid_response: Dict[str, str],
    ui_texts: ui_db_texts,
    task_code: int,
) -> Tuple[str, ListOfDBRecords, ListOfDBRecords, int]:
    """Distributes grid's modifications in two groups: remove & assign"""

    msg_error = None
    try:
        actions = grid_response[CargoKeys.actions]
        task_code += 1
        str_remove: str = actions[CargoKeys.remove]
        task_code += 1
        str_none: str = actions[CargoKeys.none]
        task_code += 1
        remove: ListOfDBRecords = []
        assign: ListOfDBRecords = []
        grid: ListOfDBRecords = grid_response[CargoKeys.grid]
        task_code += 1
        for item in grid:
            usr_new = item[MgmtCol.usr_new]
            if usr_new == str_none:
                pass
            elif usr_new != str_remove:  # new user
                assign.append(item)
            elif item[MgmtCol.usr_curr] != str_none:  # ignore remove none
                remove.append(item)

    except Exception as e:
        msg_error = format_ui_item(ui_texts, "taskPrepare", task_code, str(e))

    return msg_error, remove, assign, task_code


def _save_data_to_db(
    remove: ListOfDBRecords, update: ListOfDBRecords, batch_code: str, ui_texts: ui_db_texts, task_code: int
) -> sep_mgmt_rtn:
    """
    Saves user-made changes to the UI grid to the database
    via an 'instead-of' trigger that:
        1) updates `users`;
        2) inserts new SEPs into the `sep` table (if any), and
        3) logs the changes to the `log_user_sep` log.
    """

    from carranca import global_sqlalchemy_scoped_session

    from ..models import MgmtSepUser
    from ...common.app_context_vars import logged_user, sidekick

    msg_error = None
    assigned_by = logged_user.id
    user_not_found = []
    task_code += 1
    db_session: Session
    with global_sqlalchemy_scoped_session() as db_session:
        try:

            def __set_sep_new_user(id: int, usr_new: str | None):
                user_sep = db_session.query(MgmtSepUser).filter_by(sep_id=id).one_or_none()
                if user_sep:
                    user_sep.user_new = usr_new
                    user_sep.assigned_by = assigned_by
                    user_sep.batch_code = batch_code
                else:
                    sidekick.app_log.error(f"{__name__}: SEP with ID {id} not found, cannot update.")
                    user_not_found.append(id)

            # TODO auto remove reassignment
            task_code += 1  # 565
            for row in remove:  # first remove
                __set_sep_new_user(row[MgmtCol.sep_id], None)

            task_code += 1  # 566
            for row in update:  # then update
                __set_sep_new_user(row[MgmtCol.sep_id], row[MgmtCol.usr_new])

            task_code += 1
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            saveError = format_ui_item(ui_texts, "saveError", task_code)
            msg_error = try_get_mgd_msg(e, saveError)
            sidekick.app_log.error(msg_error)

    return "", msg_error, task_code


# eof
