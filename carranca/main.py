"""
#main.py
   Main Module following the Application Factory Pattern

   Equipe da Canoa -- 2024
   mgd 2024-10-03
"""

# cSpell:ignore sqlalchemy keepalives psycopg2

import time


def _register_blueprints(app):
    from .private.routes import bp_private
    from .public.routes import bp_public

    app.register_blueprint(bp_private)
    app.register_blueprint(bp_public)


def _register_jinja(app):
    from .helpers.route_helper import private_route, public_route

    def __get_name() -> str:
        return app.shared.config.APP_NAME

    def __get_version() -> str:
        return app.shared.config.APP_VERSION

    app.jinja_env.globals.update(
        app_version=__get_version,
        app_name=__get_name,
        private_route=private_route,
        public_route=public_route,
    )


# -------------------------------------------------------
# Main --------------------------------------------------
# -------------------------------------------------------

# Here and only here: the app_name
app_name = "Canoa"

# This should be the first message of this package
the_aperture_msg = f"{app_name} is starting in {__name__}."
print(f"{'-' * len(the_aperture_msg)}\n{the_aperture_msg}")

# check mandatory information and create
#  Global var, to simplify sharing objects
from .igniter import ignite_shared
from carranca import started

shared = ignite_shared(app_name, started)

# Flask app
from carranca import create_app  # see __init__.py

app = create_app(app_name, shared.config)
shared.display.info("The Flask app was quickly created and configured.")

# Database
from .igniter import ignite_sql_alchemy

sa = ignite_sql_alchemy(app, shared)
shared.display.info("SQLAlchemy was instantiated and the db connection was successfully tested.")

# login Manger
from flask_login import LoginManager

login_manager = LoginManager(app)
shared.display.info("Flask login manager was instantiated.")

# Keep shared alive within app
app.shared = shared.keep(app, sa, login_manager)
shared.display.info("The global var 'shared' is now ready:")
if shared.config.APP_DISPLAY_DEBUG_MSG:
    shared.display.simple(repr(shared), "", False)

# Keep shared alive within app
if shared.config.APP_DISPLAY_DEBUG_MSG and True:
    from .public.debug_info import get_debug_info
    di = get_debug_info(app, shared.config)

# Blue Prints
_register_blueprints(app)
shared.display.info("The blueprints were collected and registered within the app.")

_register_jinja(app)
shared.display.info("This app's functions were registered into Jinja.")

# Tell everybody how quick we are
elapsed = (time.perf_counter() - started) * 1000
shared.display.info(f"{app_name} is now ready for the trip. It took {elapsed:,.0f}ms to create it.")


if __name__ == "__main__":
    app.run()

# eof
