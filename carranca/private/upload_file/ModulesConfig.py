# Equipe da Canoa -- 2024
#
# mgd
# cSpell:ignore
"""
Configurable Parameters for each step of the Process

see README.md
Part of Canoa `File Validation` Processes
"""

from typing import NamedTuple

OutputFile = NamedTuple("OutputFile", name=str, ext=str)

DataValidateApp = NamedTuple(
    "DataValidateApp",
    batch=str,
    name=str,
    flags=str,
    flag_debug=str,
    na_out_folder=str,
    na_in_folder=str,
)

Email = NamedTuple("Email", cc=str, bcc=str)


class ModulesConfig:
    def __init__(self):  #: BaseConfig):
        # app `validate_data` app output file name and extension
        self.output_file = OutputFile(name="data_report", ext=".html")
        self.app = DataValidateApp(
            batch="run.bat",
            name="data_validate",
            flags="--no-spellchecker",
            flag_debug="--debug",
            na_in_folder="--input_folder",  # named argument
            na_out_folder="--output_folder",
        )
        self.email = Email(
            cc="pedro.andrade.inpe@gmail.com",
            bcc="",
        )


# eof
