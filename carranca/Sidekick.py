"""
  Sidekick
    Sidekick is class to keep easily accessible
    frequently used objects

    This object is initialized in package/__init__.py

        Sidekick objects:
        ├── config         config.Config + app.config (see sidekick.py header for more info)
        ├── app_log        Flask's app logger
        └── display        mgd's simple text display to console


    app.config vs config
    ------------------------
    `app.config` has almost all the attributes of the `config``
    *plus* those of Flask.

    So to keep it 'mode secure' and avoid 'circular imports',
    use sidekick.config

    app_log == app.Logger
    ---------------------

    v1 Shared mgd 2024-07-22,10-07
    v2 Sidekick 2024.10.23
    v3 Lifetime changed
       request and module scoped variables:
            module:   _module_sidekick
            request:  g._sidekick
            session: (not used here)
            sk = session.get('sidekick', None)
            session['sidekick'] = _recreate_sidekick()


1. **Scope**: This defines where a variable is accessible in the code. It can be local, global, or nonlocal.

2. **Lifetime**: This refers to how long a variable exists in memory. For example:
    - **Local Variables**: Exist only within a function or block and are destroyed once the function or block is exited.
    - **Global Variables**: Exist for the lifetime of the program unless explicitly deleted.
    - **Instance Variables**: Exist for the lifetime of an object instance.

3. **Persistence**: In web applications like Flask, this term is used to describe how data can be saved across multiple requests and sessions. This can involve storing data in:
    - **Sessions**: Temporarily save _user data_ across multiple requests.
    - **Databases**: Persist data for long-term storage.

4. **Context**: Specifically in Flask, it refers to the contexts available:
    - **Request Context**: Lives for the duration of a single request.
    - **Application Context**: Exists for the duration of the application.

"""

# cSpell:ignore sqlalchemy mgd appcontext

from flask import Flask
from datetime import datetime

from .helpers.Display import Display
from .DynamicConfig import DynamicConfig


# Local
_display_params = "DISPLAY_PARAMS"


# this is called once, on __init__.py:create_app->igniter::ignite_sidekick
# where it 'saves' config in a global var: Config
def create_sidekick(Config: DynamicConfig, display: Display):
    from .helpers.py_helper import get_init_params

    Config[_display_params] = get_init_params(display)
    sidekick = Sidekick(Config, display)
    return sidekick


def recreate_sidekick():
    from flask import current_app
    from carranca import Config
    from .helpers.Display import Display

    msg_error = None
    try:
        _params = Config[_display_params]
        display = Display(**_params)
    except Exception as e:
        display = Display()  # use default
        msg_error = str(e)

    sidekick = Sidekick(Config, display, current_app)
    # this helps to monitor Sidekick Lifetime
    sidekick.display.debug(f"{sidekick.__class__.__name__} was recreated.")
    if msg_error:
        sidekick.display.error(f"But using default params: {msg_error}.")

    return sidekick


class Sidekick:
    """
    A handy hub for sidekick objects
    """

    def __init__(self, config: DynamicConfig, display: Display, app: Flask = None):
        self.debugging = config.APP_DEBUGGING
        self.app_name = config.APP_NAME
        self.config = config
        self.display = display
        self.started_at = datetime.now()
        self.keep(app)

    def keep(self, app):
        # https://docs.python.org/3/library/logging.html
        self.app = app
        self.app_log = None if app is None else app.logger
        return

    def __str__(self):
        return f"{self.__class__.__name__} the py dev's companion"

    # def __repr__(self):
    #     return json.dumps(self.config__dict__, indent=4, sort_keys=True)


# eof
