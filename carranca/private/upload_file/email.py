# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore
"""
Fifth step:
  - Send an email to the user, attach the validation report.

Part of Canoa `File Validation` Processes
"""

from .Cargo import Cargo
from ..models import UserDataFiles
from ...helpers.user_helper import now_as_text
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
        email_params = {'ticket': cargo.user_data_file_key, 'when': now_as_text()}
        attachment = user_report_full_name
        task_code+= 1 # 1
        if send_email(cargo.user.email, "uploadedFile_email", email_params, attachment):
            task_code+= 1 #2
            UserDataFiles.update(cargo.user_data_file_key, email_sent = True, report_ready_at = cargo.report_ready_at)
            task_code= 0
        else:
            task_code+= 2 #3

    except Exception as e:
        error_code = task_code + 5
        msg_exception = str(e)

    error_code = 0 if task_code == 0 else ModuleErrorCode.UPLOAD_FILE_EMAIL + task_code
    return cargo.update(error_code, 'uploadFileEmailFailed', msg_exception)


#eof