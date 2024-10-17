"""
    Fifth & last step:
    - Send an email to the user, attach the validation report.

    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore

from .Cargo import Cargo
from ..models import UserDataFiles
from ...main import shared
from ...helpers.user_helper import now_as_text, now
from ...helpers.email_helper import send_email
from ...helpers.error_helper import ModuleErrorCode


def email(cargo: Cargo, user_report_full_name) -> Cargo:
    """
    Send an email to the user with the
    data_validate report attached.
    """
    error_code = 0
    msg_exception = ""
    task_code = 0
    try:
        cargo.email_started_at = now()
        task_code += 1  # 1
        receipt = cargo.pd.user_receipt
        email_body_params = {
            "user_name": cargo.user.name,
            "receipt": receipt,
            "when": now_as_text(),
        }
        send_file = user_report_full_name
        email_to = {"to": f"{cargo.user.email},{cargo.user.name}", "cc": cargo.receive_file_cfg.email.cc}

        task_code += 1  # 2
        send_email(email_to, "uploadedFile_email", email_body_params, send_file)
        shared.display.info("email: An email was sent to the user with the result of the validation.")

        task_code += 2  # 3
        UserDataFiles.update(
            cargo.table_udf_key,
            report_ready_at=cargo.report_ready_at,
            e_unzip_started_at=cargo.unzip_started_at,
            f_submit_started_at=cargo.submit_started_at,
            g_email_started_at=cargo.email_started_at,
            email_sent=True,
        )
        shared.display.info("email: The validation process record was updated with the email info.")
        task_code = 0  # !important
    except Exception as e:
        task_code += 5
        msg_exception = str(e)
        shared.app_log.fatal(
            f"There was a problem sending the results email: {msg_exception}.", exc_info=task_code
        )

    error_code = 0 if task_code == 0 else ModuleErrorCode.RECEIVE_FILE_EMAIL + task_code
    return cargo.update(error_code, "uploadFileEmail_failed", msg_exception)


# eof
