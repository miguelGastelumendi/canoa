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

OutputFile = NamedTuple('OutputFile', name=str, ext=str)

DataValidateApp = NamedTuple(
    'DataValidateApp',
    batch=str,
    name=str,
    flags=str,
    flag_debug=str,
    # named arguments
    na_out_folder=str,
    na_in_folder=str,
)

Email = NamedTuple('Email', cc=str, bcc=str)


class UploadConfig:
    def __init__(self):  #: BaseConfig):
        # app `validate_data` app output file name and extension
        self.output_file = OutputFile(name='data_report', ext='.pdf')
        self.app = DataValidateApp(
            batch='run.bat',
            name='data_validate',
            flags='--no-spellchecker',
            flag_debug='', # --debug
            na_in_folder='--input_folder',  # named argument
            na_out_folder='--output_folder',
        )
        self.email = Email(
            cc='pedro.andrade.inpe@gmail.com',
            bcc='',
        )


# eof
