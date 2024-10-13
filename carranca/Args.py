"""
 Equipe da Canoa -- 2024

 Base shared objects

 mgd 2024-10-01
 """

import json


class Args:
    def __init__(self, as_debug):
        self.app_debug = as_debug
        self.app_mode = None  # Not ready, only flags
        self.display_mute = not as_debug
        self.display_all = as_debug
        self.display_debug = as_debug
        self.display_icons = True
        self.display_mute_after_init = False

    def __repr__(self):
        return json.dumps(self.__dict__, indent=None, separators=(",", ":"), sort_keys=True)


# eof
