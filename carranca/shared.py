"""
    A shared module to easily share app and frequently
    used app's properties

    app.config vs app_config
    ------------------------
    `app.config` has all the attributes of the `app_config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    import just `app_config` instead of `app` to use app.config

    app_log == app.Logger
    ---------------------


"""
# cSpell:ignore sqlalchemy

""" usually this part is in __init__.py
    as `db` is very shared so I brought it here.
    (with ChatGPT 4.o consent ;-)
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# -----------------------------------
# Shared objects
db = SQLAlchemy()
login_manager = LoginManager()
app = None       # see __int__.py & main.py
# see update_shared_objects() below
app_config = None
app_log = None



def register_blueprints():
    from .private.routes import bp_private # carranca\private\routes.py
    app.register_blueprint(bp_private)
    from .public.routes import bp_public   # carranca\public\routes.py
    app.register_blueprint(bp_public)


def configure_database(app):
    @app.teardown_request  # Flask decorator
    def shutdown_session(exception=None):
        db.session.remove()


def register_jinja():
    from .helpers.route_helper import private_route, public_route
    def _get_name() -> str:
        app_log.debug(app_config.APP_NAME)
        return app_config.APP_NAME
    def _get_version() -> str:
        app_log.debug( app_config.APP_VERSION )
        return app_config.APP_VERSION
    app.jinja_env.globals.update(
        app_version= _get_version,
        app_name= _get_name,
        private_route= private_route,
        public_route= public_route,
    )
    # template = app.jinja_env.from_string("{{ app_name() }} - {{ app_version() }}")
    # print(template.render())
    # print(template.render(app_name=_get_name, app_version=_get_version))



def update_shared_objects(app_flask, config) -> None: # :BaseConfig
    global app, app_config, app_log

    app = app_flask
    app.config.from_object(config)

    app_config = config
    app_log = app.logger

    register_blueprints()
    configure_database(app)
    register_jinja()
    return

#eof