# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore ext
"""
Performs the complete validation process:
    - Check: file name, create folders
    - Register

Part of Canoa `File Validation` Processes
"""

from upload_file_check import upload_file_check as check
from upload_file_register import upload_file_register as register

#  task_code, log_msg, msg_success, file_ticket = upload_file_process(current_user, file_obj, valid_extensions)

class Cargo:
    name = 'cargo'
    def __init__(self, error_code: int, exception_msg: str, next, final ):
        self.error_code = error_code
        self.exception_msg = exception_msg
        self.next = next    # the next module parameters
        self.final = final  # the final result of this process


def _get_params(cargo: Cargo):
    params = cargo.next
    params[Cargo.name] = Cargo(0, '', {}, cargo.final)
    return cargo.error_code, cargo.exception_msg, next

def upload_file_process( current_user: object, file_obj: object, valid_ext: list[str]) -> object:

    params = {
        Cargo.name: Cargo(0, '', {}, {}),
        'current_user': current_user,
        'file_obj': file_obj,
        'valid_ext': valid_ext,
    }


    exception_msg = None
    error_code = 0

    for proc in [check, register, step3]:
        try:
            cargo = proc(params)
            error_code, exception_msg, params = _get_params(cargo)
            if (error_code > 0 ):
                break
        except Exception as e:
            error_code = 100 # TODO
            exception_msg = str(e)
            break

    if exception_msg:
        print(f"An error occurred: {exception_msg}")
    else:
        print(f"Final result: {cargo}"


#eof