"""
    config_validate_process.py

    ValidateProcessConfig
    Configuration of the file for validate process
    (./private/validate_process)
    Stores the configurable parameters required at each step

    see README.md
    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd

"""

# cSpell:ignore

from typing import NamedTuple
from .helpers.py_helper import OS_IS_WINDOWS, get_envvar
from .helpers.email_helper import RecipientsDic

OutputFile = NamedTuple("OutputFile", name=str, ext=str)

DataValidateApp = NamedTuple(
    "DataValidateApp",
    batch=str,
    folder=str,
    ui_name=str,  # the name of the app to display to user/log/etc
    flags=str,
    flag_debug=str,
    # named arguments
    na_user_name=str,
    na_file_name=str,
    na_schema_se=str,
    na_in_folder=str,
    na_out_folder=str,
)


class ValidateProcessConfig:
    def __init__(self, debug=False):  #: BaseConfig
        # dv_app `data_validate` app output file name and extension
        self.output_file = OutputFile(name="data_report", ext=".pdf")
        self.dv_app = DataValidateApp(
            batch="run_validate." + ("bat" if OS_IS_WINDOWS else "sh"),  # TODO: OS_IS_LINUX
            folder="data_validate",  # ./<common_folder>/<folder>/python main.py
            ui_name="data_validate",
            flags="--no-spellchecker" if OS_IS_WINDOWS else "",
            flag_debug="",  # --debug
            # named argument
            na_schema_se="--sector",
            na_user_name="--user",
            na_file_name="--file",
            na_in_folder="--input_folder",
            na_out_folder="--output_folder",
        )
        self.cc_recipients = RecipientsDic(cc=get_envvar("EMAIL_REPORT_CC"))
        self.remove_report = True  # default is true
        self.debug_process = None  # None -> set by param debug

        if self.debug_process is None:
            self.debug_process = debug


# eof
