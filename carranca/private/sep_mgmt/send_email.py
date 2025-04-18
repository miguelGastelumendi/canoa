"""
SEP Management and User assignment
Send email to the user with the list of
SEPs assigned to him/her.

Equipe da Canoa -- 2025
mgd 202-04-09
"""

# cSpell: ignore mgmt


from sqlalchemy.orm import Session

from ...helpers.py_helper import is_str_none_or_empty
from ...helpers.types_helper import ui_db_texts, sep_mgmt_rtn
from ...helpers.email_helper import RecipientsListStr
from ...helpers.ui_db_texts_helper import format_ui_item

from carranca import global_sqlalchemy_scoped_session
from ..models import MgmtEmailSep
from ...common.app_context_vars import sidekick
from ...helpers.py_helper import now
from ...helpers.sendgrid_helper import send_email


def send_email(batch_code: str, ui_texts: ui_db_texts, task_code: int) -> sep_mgmt_rtn:
    """
    Send an email for each user with a
    'new' SEP or if it was removed
    """

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
