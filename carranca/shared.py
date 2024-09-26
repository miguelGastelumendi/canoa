"""
    A shared module to easily share app and frequently
    used app's properties

    app.config vs app_config
    ------------------------
    `app.config` has all the attributes of the `app_config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    import just `app_config` instead of `app` to use app.config

    same with
        - app_log => app.Logger
        - app_db => db


    from shared import app_config
    ~form main import app~
"""

# Shared objects
app = None
app_config = None
app_log = None
db = None
#-----------------




def register_extensions():
    from carranca import login_manager
    app_db.init_app(app)
    login_manager.init_app(app)


def register_blueprints():
    from .private.routes import bp_private # carranca\private\routes.py
    app.register_blueprint(bp_private)
    from .public.routes import bp_public   # carranca\public\routes.py
    app.register_blueprint(bp_public)


def configure_database(app):
    @app.teardown_request  # Flask decorator
    def shutdown_session(exception=None):
        app_db.session.remove()


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



def create_app_and_shared_objects(config):
    from flask import Flask
    from carranca import db
    global app, app_config, app_db, app_log

    app = Flask(__name__)
    app.config.from_object(config)

    app_config = config
    app_db = db
    app_log = app.logger

    register_extensions()
    register_blueprints()
    configure_database(app)
    register_jinja()
    return app

#eof