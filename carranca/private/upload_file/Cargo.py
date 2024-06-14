# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore ext
"""
Cargo is a class that helps to control
upload_file validation process loop.

Part of Canoa `File Validation` Processes
"""

from .StorageInfo import StorageInfo
from ...upload_config import UploadConfig
from ...helpers.py_helper import is_str_none_or_empty
from ...helpers.user_helper import LoggedUser, now


class Cargo:
    name = "cargo"
    default_error = "uploadFileError"

    def __init__(
        self,
        in_debug: bool,
        user: LoggedUser,
        upload_cfg: UploadConfig,
        storage: StorageInfo,
        first: dict,
    ):
        """
        Cargo is a class that helps to control the process loop.

        Args:
            in_debug (bool):            app is in debug mode?
            user (LoggedUser):          basic user info
            upload_cfg (UploadConfig):  configuration of the file upload process modules
            storage (StorageInfo):      keeps info of the folder structure and file names
            first (dict):               parameters for the `first` module
        """
        self.init()
        self.in_debug_mode = in_debug
        self.user = user
        self.upload_cfg = upload_cfg
        self.storage = storage
        self.next = dict(first)

        self.step = 1
        self.final = {}  # the process.py return values
        """ When the process began """
        self.started_at = now()
        self.report_ready_at = None
        self.user_data_file_key = ''
        self.user_receipt = ''

    def init(self):
        """initialization of the error variables and `next module parameters` (next) at each loop"""
        self.error_code = 0
        self.msg_error = ''
        self.msg_exception = ''
        self.next = {}
        return self

    def update(
        self,
        error_code: int,
        msg_error: str = '',
        msg_exception: str = '',
        next: dict = {},
        final: dict = {},
    ) -> tuple[int, str, str, object]:
        """
        Updates the class with the 'next' procedure values

        Args:
            error_code (int):         error code (0 none)
            msg_error (str):          an entry in vw_ui_texts (see texts_helper.py[get_msg_error()])
            msg_exception (str):      exception error message, to be logged, in order to assist in the debugging process
            next (dict):              parameters for the `next` procedure
            final (dict):             collects items for the final result: `return final`

        Returns:
            tuple:
            int   error code (0 none)
            str   an entry in vw_ui_texts (see texts_helper.py[get_msg_error()])
            str   exception error message, to be logged, in order to assist in the debugging process
            obj   self, the Cargo instance
        """
        self.step += 1
        self.error_code = error_code
        self.msg_error = (
            Cargo.default_error if is_str_none_or_empty(msg_error) else msg_error
        )
        self.msg_exception = msg_exception
        self.next = dict(next)  # new next procedure parameters
        self.final.update(final)  # keep data though loops
        # TODO self.elapsed.push(now())
        return (self.error_code, self.msg_error, self.msg_exception, self)


# eof
