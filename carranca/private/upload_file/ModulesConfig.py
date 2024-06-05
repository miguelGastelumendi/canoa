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
DataApp = NamedTuple(
    "DataApp",
    batch=str,
    name=str,
    flags=str,
    flag_debug=str,
    na_out_folder=str,
    na_in_folder=str,
)
Email = NamedTuple("Email", originator=str, cc=str, bcc=str, api_key=str)


class ModulesConfig:
    def __init__(self, app_config):  #: BaseConfig):
        # app `validate_data` app output file name and extension
        self.output_file = OutputFile(name="data_report", ext=".html")
        self.app = DataApp(
            batch="run.bat",
            name="data_validate",
            flags="--no-spellchecker",
            flag_debug="--debug",
            na_in_folder="--input_folder",  # named argument
            na_out_folder="--output_folder",
        )
        self.email = Email(
            originator=app_config.EMAIL_ORIGINATOR,
            api_key=app_config.EMAIL_API_KEY,
            cc="miguelgastelumendi@hotmail.com",  #  'pedro.andrade.inpe@gmail.com',
            bcc="",
        )


# eof
