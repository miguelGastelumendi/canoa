"""
SEP Icon Configuration

Equipe da Canoa -- 2024
mgd 2024-11-15
"""

# cSpell: ignore mgmt tmpl lightgray darkgrey

from os import path
from flask import current_app
from typing import TypeAlias

from ..helpers.route_helper import static_route

SvgContent: TypeAlias = str


class SepIconConfig:

    ext = "svg"
    folder = "sep_icons"
    static_folder = path.basename(current_app.static_folder)
    local_path = path.join(current_app.static_folder, folder)
    empty_file = "sep_icon-empty.svg"
    error_file = "sep_icon-error.svg"
    none_file = "sep_icon-none.svg"

    def set_url(to: str) -> str:
        return static_route(f"{SepIconConfig.folder}/{to}")

    def content_for(
        fill_color: str, text: str = "", stroke_width: int = 1
    ) -> SvgContent:
        return (
            "<svg width='62' height='62' xmlns='http://www.w3.org/2000/svg'>"
            f"<rect width='100%' height='100%' fill='{fill_color}' stroke='black' stroke-width='{stroke_width}' />"
            f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='20' fill='black'>{text}</text>"
            "</svg>"
        )

    def empty_content() -> SvgContent:
        # see canoa.css[.grd-item-none]
        return SepIconConfig.content_for("darkgrey", "Falta")

    def error_content() -> SvgContent:
        # see canoa.css[.grd-item-remove]
        return SepIconConfig.content_for("firebrick", "Erro")

    def none_content() -> SvgContent:
        # when user has no sep assigned
        return SepIconConfig.content_for("none", "", 2)


# eof
