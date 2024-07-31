"""
    upload_config.py

    UploadConfig
    Configuration of the file upload process modules
    Stores the configurable parameters required at each step
    of the Upload Process

    see README.md

    Part of Canoa `File Validation` Processes

    Equipe da Canoa -- 2024
    mgd

"""

# cSpell:ignore

from typing import NamedTuple
from carranca.helpers.py_helper import OS_IS_LINUX, OS_IS_WINDOWS

OutputFile = NamedTuple("OutputFile", name=str, ext=str)

DataValidateApp = NamedTuple(
    "DataValidateApp",
    batch=str,
    folder=str,
    ui_name=str, # display to user/log/etc
    flags=str,
    flag_debug=str,
    # named arguments
    na_in_folder=str,
    na_out_folder=str,
)

Email = NamedTuple("Email", cc=str, bcc=str)


class UploadConfig:
    def __init__(self):  #: BaseConfig):
        # d_v `data_validate` app output file name and extension
        self.output_file = OutputFile(name="data_report", ext=".pdf")
        self.d_v = DataValidateApp(
            batch="run_validate." + ("bat" if OS_IS_WINDOWS else "sh"),  # TODO: OS_IS_LINUX
            folder="data_validate", # ./<common_folder>/<folder>/python main.py
            ui_name= "data_validate",
            flags="--no-spellchecker" if OS_IS_WINDOWS else "",
            flag_debug="",  # --debug
            na_in_folder="--input_folder",  # named argument
            na_out_folder="--output_folder",
        )
        self.email = Email(
            cc="pedro.andrade.inpe@gmail.com, Pedro Andrade;cassia.lemos@inpe.br, Cassia Lemos",
            bcc="",
        )
        self.remove_report= False # default is true


# eof
