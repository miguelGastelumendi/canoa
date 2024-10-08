"""
#main.py
   Main Module following the Application Factory Pattern

   Equipe da Canoa -- 2024
   mgd 2024-10-03
"""
# cSpell:ignore sqlalchemy keepalives

import time


def _register_blueprints(app):
    from .private.routes import bp_private
    from .public.routes import bp_public

    app.register_blueprint(bp_private)
    app.register_blueprint(bp_public)


def _register_jinja(app):
    from .helpers.route_helper import private_route, public_route

    def __get_name() -> str:
        return app.shared.app_config.APP_NAME

    def __get_version() -> str:
        return app.shared.app_config.APP_VERSION

    app.jinja_env.globals.update(
        app_version=__get_version,
        app_name=__get_name,
        private_route=private_route,
        public_route=public_route,
    )

def _create_sql_alchemy(app, app_config):
    from flask_sqlalchemy import SQLAlchemy
    sa = SQLAlchemy(app)

    # Obfuscate the password of SQLALCHEMY_DATABASE_URI value
    import re
    db_uri_safe = re.sub(
        app_config.SQLALCHEMY_DATABASE_URI_REMOVE_PW_REGEX,
        app_config.SQLALCHEMY_DATABASE_URI_REPLACE_PW_STR,
        app_config.SQLALCHEMY_DATABASE_URI,
    )

    # not need any more.
    app_config.SQLALCHEMY_DATABASE_URI= db_uri_safe
    return sa

# -------------------------------------------------------
# Main --------------------------------------------------
# -------------------------------------------------------

# Here and only here: the app_name
app_name = "Canoa"
# This should be the first message of this package
the_aperture_msg = f"{app_name} is starting in {__name__}."
print('-' * len(the_aperture_msg))
print(f"{app_name} is starting is {__name__}.")

# Global var, to simplify sharing objects
from .igniter import create_shared
from carranca import started
shared = create_shared(app_name, started)

# Flask app
from carranca import create_app  # see __init__.py
app = create_app(app_name, shared.app_config)
shared.display.info("The Flask app was quickly created and configured.")

# Database
sa = _create_sql_alchemy(app, shared.app_config)
shared.display.info("SQLalchemy was instantiated")

# login Manger
from flask_login import LoginManager
login_manager = LoginManager()
shared.display.info("Flask login manager was instantiated.")
# Keep shared alive within app
app.shared = shared.keep(app, sa, LoginManager())
shared.display.info("The global var 'shared' is now ready:")
shared.display.simple(repr(shared), '', False)


_register_blueprints(app)
shared.display.info("The blueprints were quickly registered within the app.")

_register_jinja(app)
shared.display.info("The Jinja functions were registered.")

# Tell everybody how quick we are
elapsed = (time.perf_counter() - started) * 1000
shared.display.info(f"{app_name} is ready (in {elapsed:,.0f}ms).")

#eof