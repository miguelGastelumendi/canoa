"""
SEP Icon Configuration

Equipe da Canoa -- 2024
mgd 2024-11-15
"""

# cSpell: ignore tmpl lightgray darkgrey

from os import path
from flask import current_app

from ..helpers.route_helper import static_route
from ..helpers.html_helper import url_join
from ..helpers.types_helper import svg_content


class SepIconConfig:

    ext = "svg"
    folder = "sep_icons"
    static_folder: str = path.basename(current_app.static_folder)
    local_path: str = path.join(current_app.static_folder, folder)
    empty_file = "sep_icon-empty.svg"
    error_file = "sep_icon-error.svg"
    none_file = "sep_icon-none.svg"

    def set_url(to: str) -> str:
        folder_and_name = url_join(SepIconConfig.folder, to)
        return static_route(folder_and_name)

    def content_for(fill_color: str, text: str = "", stroke_width: int = 1) -> svg_content:
        return (
            "<svg width='62' height='62' xmlns='http://www.w3.org/2000/svg'>"
            f"<rect width='100%' height='100%' fill='{fill_color}' stroke='black' stroke-width='{stroke_width}' />"
            f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='20' fill='black'>{text}</text>"
            "</svg>"
        )

    def empty_content() -> svg_content:
        # see canoa.css[.grid-item-none]
        return SepIconConfig.content_for("darkgrey", "Falta")

    def error_content() -> svg_content:
        # see canoa.css[.grid-item-remove]
        return SepIconConfig.content_for("firebrick", "Erro")

    def none_content() -> svg_content:
        # when user has no sep assigned
        return SepIconConfig.content_for("none", "", 2)


# eof
