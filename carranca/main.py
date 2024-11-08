"""
#main.py
   Main Module following the Application Factory Pattern

   Equipe da Canoa -- 2024
   mgd 2024-10-03
"""

# cSpell:ignore sqlalchemy keepalives psycopg2

import time


# -------------------------------------------------------
# Main --------------------------------------------------
# -------------------------------------------------------

# Here and only here: the app_name
app_name = "Canoa"

# This should be the first message of this package
the_aperture_msg = f"{app_name} is starting in {__name__}."
print(f"{'-' * len(the_aperture_msg)}\n{the_aperture_msg}")


# Flask app
from carranca import create_app, started  # see __init__.py

app = create_app(app_name)

from .Sidekick import sidekick

sidekick.display.info(
    "All mandatory information has been checked and is available. The app is ready to run."
)

# Keep shared alive within app
sidekick.keep(app)
sidekick.display.info("The session 'sidekick' variable is now ready for the current session.")

if sidekick.config.APP_DISPLAY_DEBUG_MSG:
    print(repr(sidekick))
    from .public.debug_info import get_debug_info

    di = get_debug_info(app, sidekick.config)  # TODO, print

# Tell everybody how quick we are
elapsed = (time.perf_counter() - started) * 1000
sidekick.display.info(f"{app_name} is now ready for the trip. It took {elapsed:,.0f}ms to create it.")

if __name__ == "__main__":
    app.run()

# eof
