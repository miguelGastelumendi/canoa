"""
 Equipe da Canoa -- 2024

"""

#cSpell:ignore SQLALCHEMY, cssless

from sys import exit
from flask_minify import Minify
from carranca import create_app
from carranca.config import Config, config_dict


# WARNING: Don't run with debug turned on in production!
# mgd went to config.py  DEBUG = (Config.getenv('DEBUG', 'False') == 'True')
#   DEBUG -> Config.DEBUG

# The configuration
get_config_mode = 'Debug' if Config.DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
host, port = app_config.SERVER_ADDRESS.split(':');


if not Config.DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if Config.DEBUG:
    app.logger.info('DEBUG            = ' + str(Config.DEBUG))
    app.logger.info('Page Compression = ' + 'FALSE' if Config.DEBUG else 'TRUE')
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT)
    app.logger.info('Host:Port        = ' +  f"{host}:{port}")


if __name__ == "__main__":
    app.run(host=host, port=int(port))

#eof
