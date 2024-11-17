"""
    SEP Icon Configuration

    Equipe da Canoa -- 2024
    mgd 2024-11-15
"""

# cSpell: ignore mgmt tmpl lightgray darkgrey

from os import path
from ..Sidekick import sidekick


class SepIconConfig:
    ext = "svg"
    folder = "sep_icons"
    path = path.join(sidekick.app.static_folder, folder)
    empty_file = "sep_icon-empty.svg"

    def set_url(to: str) -> str:
        return f"{SepIconConfig.folder}/{to}"

    def content_for(bg_color: str, text: str) -> str:
        return (
            "<svg width='62' height='62' xmlns='http://www.w3.org/2000/svg'>"
            f"<rect width='100%' height='100%' fill='{bg_color}' stroke='black' stroke-width='1' />"
            f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='20' fill='black'>{text}</text>"
            "</svg>"
        )

    def empty_content():
        # see canoa.css[.grd-item-none]
        return SepIconConfig.content_for("darkgrey", "Falta")

    def error_content():
        # see canoa.css[.grd-item-remove]
        return SepIconConfig.content_for("firebrick", "Erro")


# eof
