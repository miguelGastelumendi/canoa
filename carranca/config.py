"""
 Equipe da Canoa -- 2024

 Configuration Files for the Application

 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
 mgd 2024-10-11: Base went to it's own file
"""

# cSpell:ignore SQLALCHEMY searchpath

from os import environ
from hashlib import sha384

from .BaseConfig import BaseConfig, app_mode_development, app_mode_production
from .helpers.py_helper import is_str_none_or_empty
from .helpers.wtf_helper import LenValidate

# Get the Jinja Template folder name
def _get_template_folder():
    from jinja2 import Environment, FileSystemLoader

    # Create a Jinja2 environment using a specific template folder
    env = Environment(loader=FileSystemLoader("templates"))
    # Access the template folder path
    template_folder = env.loader.searchpath[0]
    return template_folder


# Environment Variables for the config
def _init_envvar_of_config(cfg, fuse):
    """
    Initialize BaseConfig
    from environment variables
    """
    for key, value in environ.items():
        attribute_name = key[len(fuse.envvars_prefix) :]
        if not key.startswith(fuse.envvars_prefix):
            pass
        elif hasattr(cfg, attribute_name):
            value = bool(value) if value.capitalize() in [str(True), str(False)] else value
            if is_str_none_or_empty(value):
                fuse.display.warn(f"Ignoring empty envvar value for key [{key}], keeping original.")
            else:
                setattr(cfg, attribute_name, value)
        elif cfg.APP_DEBUG:
            fuse.display.warn(
                f"[{attribute_name}] is not an attribute of `Config`, will not set envvar value."
            )

class DynamicConfig(BaseConfig):

    def __init__(self):
        from .igniter import fuse

        _init_envvar_of_config(self, fuse)
        fuse.display.info(f"Config {self.APP_MODE} was instantiated.")
        self.TEMPLATES_FOLDER =  _get_template_folder()

        # min & max text length for pw & user_name
        self.len_val_for_pw = LenValidate(6, 22)
        self.len_val_for_uname = LenValidate(3, 22)
        self.len_val_for_email = LenValidate(8, 60)

        # initialize special attributes

        def _if_debug(attrib):
            return bool(bool(self.APP_PROPAGATE_DEBUG) if attrib is None else attrib)

        self.APP_DEBUG = _if_debug(self.APP_DEBUG)
        self.APP_MINIFIED = _if_debug(self.APP_MINIFIED)
        self.APP_DISPLAY_DEBUG_MSG = _if_debug(self.APP_DISPLAY_DEBUG_MSG)
        self.APP_DEBUG = _if_debug(self.APP_DEBUG)
        self.DEBUG_TEMPLATES = _if_debug(self.DEBUG_TEMPLATES)
        if is_str_none_or_empty(self.SECRET_KEY):
            """
            SECRET_KEY
            used for securely signing the session cookie (mgd: change every version)
            https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY
            """
            unique = f"{DynamicConfig.APP_NAME} v{DynamicConfig.APP_VERSION}".encode()
            self.SECRET_KEY = sha384(unique).hexdigest()


# === Development Config
class DevelopmentConfig(DynamicConfig):
    """
    The Debug Configuration Class for the App
    """

    APP_PROPAGATE_DEBUG =True
    APP_MODE = app_mode_development

    # == Flask ==
    SERVER_ADDRESS = (
        # All IPs at port 5001
        "http://0.0.0.0:5001"
        if is_str_none_or_empty(BaseConfig.SERVER_ADDRESS)
        else BaseConfig.SERVER_ADDRESS
    )


# Production Config
class ProductionConfig(DynamicConfig):
    """
    The Production Configuration Class for the App
    """

    APP_PROPAGATE_DEBUG = False
    APP_DEBUG = False
    APP_MODE = app_mode_production


def get_config_for_mode(app_mode: str) -> DynamicConfig:
    """
    Return the appropriated cOnfiguration
    """
    config = None
    if app_mode == app_mode_production:
        config= ProductionConfig()
    elif app_mode == app_mode_development:
        config= DevelopmentConfig()
    else:
        return None

    return config

# eof
