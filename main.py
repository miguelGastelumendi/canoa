"""
    The main script ;-)

    For newbies, remember:
        project_root/
        ├── main.py      # <- You are here
        ├── App/         # Optional folder for application logic
        │   └── ...      # Other files in the App folder
        └── other_files.py  # Other Python files in the root directory

    see https://flask.palletsprojects.com/en/latest/tutorial/factory/


    Equipe da Canoa -- 2024
    mgd
"""
 #cSpell:ignore SQLALCHEMY, cssless sendgrid

from sys import exit
from flask_minify import Minify
from urllib.parse import urlparse

from carranca import create_app
from carranca.config import config_modes, BaseConfig, app_mode_production, app_mode_debug

from carranca.helpers.py_helper import is_str_none_or_empty, coalesce

# WARNING: Don't run with debug turned on in production!
app_mode = BaseConfig.get_os_env('APP_MODE', app_mode_debug)
app_config = None

try:
    app_config = config_modes[app_mode]

except KeyError:
    exit(f"Error: Invalid <app_mode>. sendgrid [{app_mode_debug}, {app_mode_production}].")


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

def __log_and_exit( ups ):
    app.logger.error(ups)
    exit(ups)

def __is_empty(key: str) -> bool:
    value = getattr(app_config, key, '')
    empty = (value is None or value.strip() == '')
    if empty:
        app.logger.error(f"Key [{key}] has no value.")
    return empty

# Check that the mandatory environment variables are set.
if __is_empty('SQLALCHEMY_DATABASE_URI') or  __is_empty('SERVER_ADDRESS') or __is_empty('SECRET_KEY'):
    __log_and_exit('Mandatory environment variables were not set.')

# Check Server address, in windows protocol is not mandatory
host = ''
port = 0
server_address = ''
default_scheme = 'http://'
try:
    server_address = app_config.SERVER_ADDRESS
    address = urlparse(server_address, default_scheme)
    print(address)
    host = address.hostname
    port = address.port
    print(address.port)
except Exception as e:
    app.logger.error(f"`urlparse('{server_address}', '{default_scheme}') -> parsed: {address.hostname}:{address.port}`")
    __log_and_exit(f"Error parsing server address. Expect value is `[scheme|protoco]HostName:Port` , found: [{app_config.SERVER_ADDRESS}]. Error {e}")


# Minified html/js if in production
minified = False
if not app_config.DEBUG:
    Minify(app=app, html=True, js=True, cssless=False)
    minified = True

# TODO Argument --info
app.logger.info('--------------------')
app.logger.info(f"{app_config.app_name} started {app_config.app_mode} in mode :-).")
if app_config.DEBUG:
    app.logger.info(f"DEBUG            : {app_config.DEBUG}")
    app.logger.info(f"Page Compression : {minified}")
    app.logger.info(f"Database address : {app_config.SQLALCHEMY_DATABASE_URI}")
    app.logger.info(f"ASSETS_ROOT      : {app_config.ASSETS_ROOT}")
    app.logger.info(f"Server address   : {host}:{port}")
    app.logger.info(f"External address : {coalesce(app_config.SERVER_EXTERNAL_IP, '<set on demand>')}")
    app.logger.info(f"External port    : {coalesce(app_config.SERVER_EXTERNAL_PORT, '<none>')}")

# if is_str_none_or_empty(app_config.EMAIL_API_KEY):
#     app.logger.warning(f'Sendgrid API key was not found, the app will not be able to send emails.')

# if is_str_none_or_empty(app_config.EMAIL_ORIGINATOR):
#     app.logger.warning(f'The app email originator is not defined, the app will not be able to send emails.')


print(port)
print(host)    

if __name__ == '__main__':
    print(port)
    print(host)    
    app.run(host=host, port=port, debug=app_config.DEBUG)
    

# eof
