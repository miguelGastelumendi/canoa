"""
 Equipe da Canoa -- 2024
    see https://flask.palletsprojects.com/en/latest/tutorial/factory/
"""
#cSpell:ignore SQLALCHEMY, cssless

from sys import exit
from flask_minify import Minify
from urllib.parse import urlparse

from . import create_app

from .config import config_modes, BaseConfig, app_mode_production, app_mode_debug


# WARNING: Don't run with debug turned on in production!
app_mode = BaseConfig.get_os_env("APP_MODE", app_mode_debug)
app_config = None

try:
    app_config = config_modes[app_mode]

except KeyError:
    exit(f"Error: Invalid <app_mode>. Expected a value from [{app_mode_debug}, {app_mode_production}].")


app = create_app(app_config)
"""
    app.config vs app_config
    ------------------------
    `app.config` has all the attributes of the `app_config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    import just `app_config` instead of `app` to use app.config

    from main import app_config
    ~form main import app~

"""
def _empty(key: str) -> bool:
    value = getattr(app_config, key)
    empty = (value is None or value.strip() == '')
    if empty:
        print(key)
    return empty


# Check basic info
if _empty("SQLALCHEMY_DATABASE_URI") or _empty("EMAIL_API_KEY") or _empty("SERVER_ADDRESS") or _empty("SECRET_KEY"):
    """ Check if you have the basic information for proper operation """
    exit("Verifique se as variáveis de ambiente estão definidas.")


# Minified html/js if in production
minified = False
if not app_config.DEBUG:
    Minify(app=app, html=True, js=True, cssless=False)
    minified = True

# TODO Argument --info

# Display debug info
app.logger.info('-----------------')
app.logger.info(f"{app_config.app_name} started {app_config.app_mode} in mode :-).")
if app_config.DEBUG:
    app.logger.info(f"DEBUG            : {app_config.DEBUG}")
    app.logger.info(f"Page Compression : {minified}")
    app.logger.info(f"Database address : {app_config.SQLALCHEMY_DATABASE_URI}")
    app.logger.info(f"ASSETS_ROOT      : {app_config.ASSETS_ROOT}")
    app.logger.info(f"Server address   : {app_config.SERVER_ADDRESS}")
    app.logger.info(f"External address : {app_config.SERVER_EXTERNAL_IP}")


# Prepare for lunching...
address = urlparse(app_config.SERVER_ADDRESS)
host = address.hostname
port = int(address.port)

# Go!
if __name__ == "__main__":
    app.run(host=host, port=port, debug=app_config.DEBUG)

#eof
