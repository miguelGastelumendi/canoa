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
from ...helpers.user_helper import now_as_text, get_user_receipt
from ...helpers.email_helper import send_email
from ...helpers.error_helper import ModuleErrorCode


def email(cargo: Cargo, user_report_full_name) -> Cargo:
    """
    Send an email to the user with the
    data_validate report attached.
    """
    error_code = 0
    msg_exception = ''
    task_code = 0

    try:
        task_code += 1  # 1
        receipt =  get_user_receipt(cargo.final['file_ticket'])
        email_body_params = {'user_name': cargo.user.name, 'receipt': receipt, 'when': now_as_text()}
        send_file = user_report_full_name
        email_to = {'to': cargo.user.email, 'cc': cargo.receive_file_cfg.email.cc}

        task_code += 1  # 2
        send_email(email_to, 'uploadedFile_email', email_body_params, send_file)

        task_code += 2  # 3
        UserDataFiles.update(
            cargo.user_data_file__key,
            email_sent=True,
            report_ready_at=cargo.report_ready_at,
        )
        task_code = 0  # !important
    except Exception as e:
        task_code += 5
        msg_exception = str(e)

    error_code = 0 if task_code == 0 else ModuleErrorCode.RECEIVE_FILE_EMAIL + task_code
    return cargo.update(error_code, 'uploadFileEmailFailed', msg_exception)


# eof
