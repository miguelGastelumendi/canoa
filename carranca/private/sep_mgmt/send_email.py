"""
SEP Management and User Assignment
This module handles sending emails to users regarding their
 assignment or removal of Strategic Sectors (SEPs).

Emails are sent to notify users when a new SEP is assigned
 to them or when a SEP is removed from their management.

Developed by the Canoa Team -- 2025
mgd 2025-04-09
Last Modified: 2025-11-06
"""

# cSpell: ignore mgmt


from typing import Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from carranca import global_sqlalchemy_scoped_session
from ...models.private import MgmtEmailSep
from ...helpers.types_helper import UiDbTexts, SepMgmtReturn, OptStr
from ...helpers.email_helper import RecipientsDic, RecipientsListStr
from ...common.app_context_vars import sidekick
from ...helpers.gmail_api_helper import send_mail
from ...helpers.ui_db_texts_helper import format_ui_item
from ...common.app_error_assistant import proper_user_exception

def send_email(batch_code: str, ui_texts: UiDbTexts, task_code: int) -> SepMgmtReturn:
    """
    Send an email for each user with a
    'new' SEP or if it was removed
    """

    task_code += 1  # 568
    msg_error = None
    db_session: Session
    with global_sqlalchemy_scoped_session() as db_session:
        try:
            # The users involved in the batch attribution (`batch_code`).
            mgmt_email_list = (
                db_session.query(MgmtEmailSep).filter_by(batch_code=batch_code).all()
            )
            if not mgmt_email_list:
                return None, ui_texts["emailNone"], task_code

            texts = {}
            texts["subject"] = ui_texts["emailSubject"]

            def _send_email( email: str, to_user: str, se: str, content_id: str ) -> OptStr:
                msg_error = None  # maybe is a second try to send email, so clear it
                try:
                    # Prezado {0},<br><br>A partir desta data, o Setor Estratégico '{1}' ...
                    texts["content"] = format_ui_item(ui_texts, content_id, to_user, se)
                    recipients = RecipientsDic(to=RecipientsListStr(email, to_user))
                    subject = ui_texts["subject"]
                    content = ui_texts["content"]

                    if not send_mail(recipients, subject, content):
                        msg_error: str = ui_texts["emailSilentError"]
                except Exception as e:
                    # error_count += 1
                    msg_error = str(e)
                return msg_error

            def _e(email: str, error: str) -> str:
                return f"{email}:[{(error if error else 'OK')}]/n"

            for item in mgmt_email_list:
                item.email_at = func.now()
                new_error = None
                old_error = None
                sep = item.sep_fullname
                if item.new_user_name is not None:
                    new_error = _send_email(
                        item.new_user_email, item.new_user_name, sep, "emailSetNew"
                    )

                if item.old_user_name is not None:
                    old_error = _send_email(
                        item.old_user_email, item.old_user_name, sep, "emailRemoved"
                    )

                if item.new_user_name is None and item.old_user_name is None:
                    item.email_error = "No users found to send email."
                elif new_error is None and old_error is None:
                    item.email_error = None
                else:
                    item.email_error = (
                        _e(item.new_user_email, new_error)
                        + _e(item.old_user_email, old_error)
                    ).strip()

            db_session.commit()

        except Exception as e:
            db_session.rollback()
            msg_error = format_ui_item(
                ui_texts,
                "emailException",
                task_code,
                proper_user_exception(e, task_code),
            )
            sidekick.app_log.error(msg_error)

    return ui_texts["emailSuccess"], msg_error, task_code

# eof
