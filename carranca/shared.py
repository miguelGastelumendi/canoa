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
# cSpell:ignore sqlalchemy keepalives

""" usually this part is in __init__.py
    as `db` is very shared so I brought it here.
    (with ChatGPT 4.o consent ;-)
"""

# -----------------------------------
# Shared objects
# see do_db_and_share_objects(a, c)
db = None
db_engine = None
login_manager = None
app = None   # see __int__.py & main.py
app_config = None
app_log = None

def register_blueprints():
    from .private.routes import bp_private # carranca\private\routes.py
    app.register_blueprint(bp_private)
    from .public.routes import bp_public   # carranca\public\routes.py
    app.register_blueprint(bp_public)



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



def do_db_and_shared_objects(app_flask, config) -> None: # :BaseConfig
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import LoginManager
    from sqlalchemy import create_engine

    global app, app_config, app_log, db, db_engine, login_manager

    app = app_flask
    app_config = config
    app_log = app.logger

    db = SQLAlchemy()
    login_manager = LoginManager()

    db_engine = create_engine(
        app_config.SQLALCHEMY_DATABASE_URI,
        isolation_level= 'AUTOCOMMIT', # "READ UNCOMMITTED", # mgd em Canoa, acho desnecessário
        pool_pre_ping= True,
        connect_args={
            # (https://www.postgresql.org/docs/current/libpq-connect.html)
            # Maximum time to wait while connecting, in seconds  was 600.
            # instead mhd is using `pool_pre_ping` and set connect_timeout to 10
            'connect_timeout': 10
            ,'application_name': app_config.APP_NAME
            ,'keepalives': 1
        }

    )
    app_config.SQLALCHEMY_DATABASE_URI = None
    register_blueprints()
    register_jinja()
    """ ChatGPT
    During each request:
        Flask receives the request.
        Your view logic runs, interacting with the database through app_db.
        Once the response is ready, the shutdown_session() is called,
        which removes the session to prevent any lingering database connections or transactions.
    """
    @app.teardown_request  # Flask decorator, remove session after
    def shutdown_session(exception=None):
        db.session.remove()

    return

#eof