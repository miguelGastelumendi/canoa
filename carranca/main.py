"""
main.py
  Main Module following the Application Factory Pattern

  Equipe da Canoa -- 2024
  mgd 2024-10-03
"""

# cSpell:ignore sqlalchemy keepalives

import time
from .common.app_constants import APP_NAME, APP_VERSION

# -------------------------------------------------------
# Main --------------------------------------------------
# -------------------------------------------------------
# This should be the first message of this package
the_aperture_msg = f"{APP_NAME} is starting in {__name__}."
print(f"{'-' * len(the_aperture_msg)}\n{the_aperture_msg}")


# Flask app
from . import create_app, started  # see __init__.py

app, sidekick = create_app()

sidekick.display.info("All mandatory information has been checked and is available.")
sidekick.display.info("The app is ready to run!")


if sidekick.config.APP_DISPLAY_DEBUG_MSG:
    # print(repr(sidekick))
    from .public.debug_info import get_debug_info

    di = get_debug_info(app, sidekick.config)  # TODO, print

# Tell everybody how quick we are
elapsed = (time.perf_counter() - started) * 1000
sidekick.display.info(
    f"{APP_NAME} version {APP_VERSION} is now ready for the journey. It took {elapsed:,.0f} ms to create and initialize it."
)

# -------------------------------------------
# /i\
# -------------------------------------------
# on the server, __name__ is 'carranca.main'
# the app is executed by
# `canoa\.vscode\launch.json`

app_debug = sidekick.config.APP_DEBUG
app_reload = sidekick.config.APP_AUTO_RELOAD

if not __name__ == "__main__":
    sidekick.display.warn("This module is not running as `__main__`, will not run the app.")

else:
    app.run(debug=app_debug)

# TODO use wathcfiles to reload the app
# elif if app_debug and not

#     if sidekick.config.APP_AUTO_RERUN and app_debug:
#         sidekick.display.warning(
#             "You are running the app with both debug and auto-reload. This is not recommended."
#         )
#     app.run(debug=app_debug)

# eof
