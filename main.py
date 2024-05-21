"""
 Equipe da Canoa -- 2024

"""

#cSpell:ignore SQLALCHEMY, cssless

from sys import exit
from flask_minify import Minify
from carranca import create_app
from carranca.config import config_modes, BaseConfig

# WARNING: Don't run with debug turned on in production!
app_mode = BaseConfig.get_os_env("APP_MODE", 'Production')

try:
    # Load the configuration using the default values
    app_config = config_modes[app_mode]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')


app = create_app(app_config)
"""
    == config ==
    `app.config` has all the attributes of the `app_config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    import just `app_config` instead of `app` to use app.config

    from main import app_config
    ~form main import app~

"""
def _empty(n: str):
    s = getattr(app_config, n)
    empty= True if s is None or s.strip() == '' else False
    if empty:
        print(n)
    return empty


if _empty("SQLALCHEMY_DATABASE_URI") or _empty("EMAIL_API_KEY") or _empty("SERVER_ADDRESS") or _empty("SECRET_KEY"):
    exit("Verifique se as variáveis de ambiente estão definidas.")

host, port = app_config.SERVER_ADDRESS.split(':')


if not app_config.DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if app_config.DEBUG:
    app.logger.info('DEBUG            = ' + str(app_config.DEBUG))
    app.logger.info('Page Compression = ' + str(app_config.DEBUG).upper())
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT)
    app.logger.info('Host:Port        = ' +  f"{host}:{port}")

if __name__ == "__main__":
    app.run(host=host, port=int(port), debug=app_config.DEBUG)

#eof
