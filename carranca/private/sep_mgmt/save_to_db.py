"""
SEP Management and User Assignment
Handles saving user-assigned cargo data from the front end to the database.

Equipe da Canoa -- 2025
Last modified: 2023-04-09
mgd 202-04-09
"""

# cSpell: ignore mgmt

from typing import Tuple

from sqlalchemy.orm import Session

from ...helpers.py_helper import is_str_none_or_empty
from ...helpers.db_helper import try_get_mgd_msg
from ...helpers.types_helper import ui_db_texts, sep_mgmt_rtn, cargo_list, OptStr
from ...helpers.ui_db_texts_helper import format_ui_item

from .keys_values import SepMgmtGridCols, CargoKeys


def save_data(
    grid_response: cargo_list,
    batch_code: str,
    ui_texts: ui_db_texts,
    task_code: int,
) -> sep_mgmt_rtn:  # msg_success, msg_error, task_code
    """Saves user modifications to the DB via the view's trigger"""

    msg_success = None
    msg_error = None
    try:
        msg_error, remove, assign, task_code = _prepare_data_to_save(
            grid_response, ui_texts, task_code
        )
        if not is_str_none_or_empty(msg_error):
            return "", msg_error, task_code
        elif len(remove) + len(assign) == 0:
            return ui_texts["tasksNothing"], "", task_code

        task_code += 1  # 561
        _, msg_error, task_code = _save_data_to_db(
            remove, assign, batch_code, ui_texts, task_code
        )
        task_code += 1  # 565
        if is_str_none_or_empty(msg_error):
            msg_success = format_ui_item(
                ui_texts, "tasksSuccess", len(remove), len(assign)
            )
    except Exception as e:
        msg_error = format_ui_item(ui_texts, "tasksError", task_code, str(e))

    return msg_success, msg_error, task_code


def _prepare_data_to_save(
    grid_response: cargo_list,
    ui_texts: ui_db_texts,
    task_code: int,
) -> Tuple[str, cargo_list, cargo_list, int]:
    """Distributes grid's modifications in two groups: remove & assign"""

    msg_error = None
    remove: cargo_list = []
    assign: cargo_list = []
    try:
        actions = grid_response[CargoKeys.actions]
        task_code += 1
        str_none: str = actions[CargoKeys.none]
        task_code += 1
        grid: cargo_list = grid_response[CargoKeys.cargo]
        task_code += 1
        for item in grid:
            usr_new = item[SepMgmtGridCols.usr_new]
            usr_curr = item[SepMgmtGridCols.usr_curr]
            if usr_new == usr_curr:
                pass
            elif usr_new == str_none:  # remove: usr_curr -> none
                remove.append(item)
            else:  # ignore remove none
                assign.append(item)

    except Exception as e:
        msg_error = format_ui_item(ui_texts, "taskPrepare", task_code, str(e))

    return msg_error, remove, assign, task_code


def _save_data_to_db(
    remove: cargo_list,
    update: cargo_list,
    batch_code: str,
    ui_texts: ui_db_texts,
    task_code: int,
) -> sep_mgmt_rtn:
    """
    Saves user-made changes to the UI grid to the database
    via an 'instead-of' trigger that:
        1) updates `users`;
        2) inserts new SEPs into the `sep` table (if any), and
        3) logs the changes to the `log_user_sep` log.
    """

    from carranca import global_sqlalchemy_scoped_session

    from ...models.private import MgmtSepsUser
    from ...common.app_context_vars import app_user, sidekick

    msg_error = None
    assigned_by = app_user.id
    user_not_found = []
    task_code += 1
    db_session: Session
    with global_sqlalchemy_scoped_session() as db_session:
        try:

            def __set_sep_new_user(id: int, usr_new: OptStr):
                user_sep = db_session.query(MgmtSepsUser).filter_by(id=id).one_or_none()
                if user_sep:
                    user_sep.user_new = usr_new
                    user_sep.assigned_by = assigned_by
                    user_sep.batch_code = batch_code
                else:
                    sidekick.app_log.error(
                        f"{__name__}: SEP with ID {id} not found, cannot update."
                    )
                    user_not_found.append(id)

            # TODO auto remove reassignment
            task_code += 1  # 565
            for row in remove:  # first remove
                __set_sep_new_user(row[SepMgmtGridCols.sep_id], None)

            task_code += 1  # 566
            for row in update:  # then update
                __set_sep_new_user(
                    row[SepMgmtGridCols.sep_id], row[SepMgmtGridCols.usr_new]
                )

            task_code += 1
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            saveError = format_ui_item(ui_texts, "saveError", task_code)
            msg_error = try_get_mgd_msg(e, saveError)
            sidekick.app_log.error(str(e))

    return "", msg_error, task_code


# eof
