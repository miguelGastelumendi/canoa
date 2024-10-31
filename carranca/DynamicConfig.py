"""
 Equipe da Canoa -- 2024

 Configuration Files for the Application

 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
 mgd 2024-10-11: Base went to it's own file
"""

# cSpell:ignore SQLALCHEMY searchpath

from typing import Any
from os import environ
from hashlib import sha384

from .BaseConfig import BaseConfig, app_mode_development, app_mode_production
from .helpers.py_helper import as_bool, is_str_none_or_empty
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
    envvars_prefix = f"{fuse.app_name}_".upper()
    t = str(True).lower()
    f = str(False).lower()
    for key, value in environ.items():
        attribute_name = key[len(envvars_prefix) :]
        if not key.upper().startswith(envvars_prefix):
            pass
        elif not hasattr(cfg, attribute_name):
            fuse.display.debug(
                f"[{attribute_name}] is not an attribute of `Config`, will not set envvar value."
            )
        elif is_str_none_or_empty(value):
            fuse.display.warn(f"Ignoring empty envvar value for key [{key}], keeping original.")
        else:
            _value = as_bool(value) if value.lower() in [t, f, 't', '1'] else value
            setattr(cfg, attribute_name, _value)


class DynamicConfig(BaseConfig):

    def __init__(self):
        from .igniter import fuse

        # flask has config.from_prefixed_env() that us used in create_app
        # but I need one now, and displaying some msg.
        _init_envvar_of_config(self, fuse)
        fuse.display.info(f"Config {self.APP_MODE} was instantiated.")
        self.TEMPLATES_FOLDER = _get_template_folder()

        # min & max text length for pw & user_name
        self.len_val_for_pw = LenValidate(6, 22)
        self.len_val_for_uname = LenValidate(3, 22)
        self.len_val_for_email = LenValidate(8, 60)

        # initialize special attributes
        self.APP_DEBUG = as_bool(self.APP_DEBUG, False)
        self.DEBUG = as_bool(self.DEBUG, self.APP_DEBUG)

        # propagate APP_DEBUG
        def _if_debug(attrib, default=self.APP_DEBUG):
            return default if attrib is None else as_bool(attrib)

        if self.APP_PROPAGATE_DEBUG:
            self.TESTING = _if_debug(self.TESTING)  # Flask
            self.APP_MINIFIED = _if_debug(self.APP_MINIFIED, not self.APP_DEBUG)
            self.DEBUG_TEMPLATES = _if_debug(self.DEBUG_TEMPLATES)  # jinja
            self.APP_DISPLAY_DEBUG_MSG = _if_debug(self.APP_DISPLAY_DEBUG_MSG)

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

    APP_MODE = app_mode_development
    APP_DEBUG = True
    APP_PROPAGATE_DEBUG = True

    SERVER_ADDRESS = "127.0.0.1:5000"


# Production Config
class ProductionConfig(DynamicConfig):
    """
    The Production Configuration Class for the App
    """

    APP_MODE = app_mode_production
    APP_DEBUG = False
    APP_PROPAGATE_DEBUG = False
    SERVER_ADDRESS = "192.168.0.1:54754"


# Config factory by mode, add others
def get_config_for_mode(app_mode: str) -> DynamicConfig:
    """
    Return the appropriated cOnfiguration
    """
    config = None
    if app_mode == app_mode_production:
        config = ProductionConfig()
    elif app_mode == app_mode_development:
        config = DevelopmentConfig()

    return config


# eof
