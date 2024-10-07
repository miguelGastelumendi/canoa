"""
 Equipe da Canoa -- 2024

 Base shared objects

 mgd 2024-10-01
 """

# cSpell:ignore

class Args:
    def __init__(self, as_debug):
        self.debug = as_debug
        self.display_mute = not as_debug
        self.display_all = as_debug
        self.display_debug = as_debug
        self.display_icons = True
        self.display_mute_after_init = not as_debug

# eof
