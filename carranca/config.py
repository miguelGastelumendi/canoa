"""
 Equipe da Canoa -- 2024

 Configuration Files for the Application

 mgd 2024-05-06
 mgd 2024-05-21: Base, Debug, Production
 mgd 2024-10-11: Base went to it's own file
"""

# cSpell:ignore SQLALCHEMY searchpath

from typing import Dict

from .BaseConfig import BaseConfig, app_mode_development, app_mode_production
from .helpers.py_helper import is_str_none_or_empty


# === Development Config
class DevelopmentConfig(BaseConfig):
    """
    The Debug Configuration Class for the App
    """

    APP_DEBUG = True
    APP_MODE = app_mode_development

    # == Flask ==
    DEBUG = True
    TESTING = True
    SERVER_ADDRESS = (
        # All IPs at port 5001
        "http://0.0.0.0:5001"
        if is_str_none_or_empty(BaseConfig.SERVER_ADDRESS)
        else BaseConfig.SERVER_ADDRESS
    )


# Production Config
class ProductionConfig(BaseConfig):
    """
    The Production Configuration Class for the App
    """

    APP_DEBUG = False
    APP_MODE = app_mode_production
    # == Flask ==
    DEBUG = False  # Just to be sure & need some code here
    TESTING = False


def get_config_for_mode(app_mode: str) -> BaseConfig:
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

    config.initialize()
    return config

# eof
