"""
    A shared class to easily share app and frequently
    used app's properties & other objects

    This object is initialized in package/__init__.py

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

from datetime import datetime
from copy import copy as copy_str

class Shared:
    def __init__(self):
        self.app = None # see __int__.py & main.py
        self.app_config = None
        self.app_log = None
        self.db = None
        self.db_engine = None
        self.login_manager = None
        self.started_at = datetime.now()
        self.app_started_at =None

    def _create_engine(self) -> any:
        from sqlalchemy import create_engine
        result = create_engine(
            copy_str(self.app_config.SQLALCHEMY_DATABASE_URI),
            isolation_level= 'AUTOCOMMIT', # "READ UNCOMMITTED", # mgd em Canoa, acho desnecessário
            pool_pre_ping= True,
            connect_args={
                # (https://www.postgresql.org/docs/current/libpq-connect.html)
                # Maximum time to wait while connecting, in seconds  was 600.
                # instead mhd is using `pool_pre_ping` and set connect_timeout to 10
                'connect_timeout': 10
                ,'application_name': self.app_config.APP_NAME
                ,'keepalives': 1
            }
        )
        # not need any more.
        self.app_config.SQLALCHEMY_DATABASE_URI = None
        return result

    def _register_blueprints(self):
        from .private.routes import bp_private
        from .public.routes import bp_public
        self.app.register_blueprint(bp_private)
        self.app.register_blueprint(bp_public)

    def _register_jinja(self):
        from .helpers.route_helper import private_route, public_route
        def __get_name() -> str:
            self.app_log.debug(self.app_config.APP_NAME)
            return self.app_config.APP_NAME
        def __get_version() -> str:
            self.app_log.debug( self.app_config.APP_VERSION )
            return self.app_config.APP_VERSION
        self.app.jinja_env.globals.update(
            app_version= __get_version,
            app_name= __get_name,
            private_route= private_route,
            public_route= public_route,
        )

    def bind(self):
        self._register_blueprints()
        self._register_jinja()

    def initialize(self, app_config, display):
        # this is called from  __init__.py
        self.app = flask_app
        self.app_log = flask_app.logger
        self.app_config = app_config
        self.display = display

        from flask_sqlalchemy import SQLAlchemy
        self.db = SQLAlchemy()
        self.db_engine = self._create_engine()

        from flask_login import LoginManager
        self.login_manager = LoginManager()

        """ ChatGPT
        During each request:
            Flask receives the request.
            Your view logic runs, interacting with the database through app_db.
            Once the response is ready, the shutdown_session() is called,
            which removes the session to prevent any lingering database connections or transactions.
        """
        @self.app.teardown_request
        def shutdown_session(exception=None):
            self.db.session.remove()

#eof