"""
#main.py
   Main Module following the Application Factory Pattern

   Equipe da Canoa -- 2024
   mgd 2024-10-03
"""


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


import time
from carranca import create_app, started
from .igniter import create_shared

app_name = "Canoa"
print(f"{app_name} is starting is {__name__}.")
shared = create_shared(app_name, started)

app = create_app(app_name)
shared.display.info("The Flask app was nicely created.")
app.config.from_object(shared.app_config)
app.shared = shared

shared.app_log = app.logger
_register_blueprints(app)
shared.display.info("The blueprints were quickly registered.")
_register_jinja(app)
shared.display.debug("The Jinja function were registered.")

elapsed = (time.perf_counter() - started) * 1000
shared.display.info(f"{app_name} is ready (in {elapsed:,.0f}ms).")

#eof