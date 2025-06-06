"""
SEP Icon Configuration

Equipe da Canoa -- 2024
mgd 2024-11-15
"""

# cSpell: ignore tmpl lightgray darkgrey

from os import path
from flask import current_app

from ..helpers.html_helper import url_join
from ..helpers.route_helper import static_route
from ..helpers.types_helper import svg_content


class class_property(property):
    def __get__(self, instance, owner):
        return self.fget(owner)


class SepIconConfig:

    ext = "svg"
    folder = "sep_icons"
    static_folder: str = path.basename(current_app.static_folder)
    local_path: str = path.join(current_app.static_folder, folder)
    empty_file = "sep_icon-empty.svg"
    error_file = "sep_icon-error.svg"
    none_file = "sep_icon-none.svg"

    @staticmethod
    def get_icon_url(icon_file_name: str) -> str:
        folder_and_name = url_join(SepIconConfig.folder, icon_file_name)
        url = static_route(folder_and_name)
        return url

    @staticmethod
    def get_local_name(icon_file_name: str) -> str:
        local_name = path.join(SepIconConfig.local_path, icon_file_name)
        return local_name

    @staticmethod
    def content_for(
        fill_color: str,
        text: str = "",
        stroke_width: int = 2,
        fill_opacity: str = "1",
        stroke_opacity: str = "1",
    ) -> svg_content:
        return (
            "<svg width='64' height='64' xmlns='http://www.w3.org/2000/svg'>"
            f"<rect width='100%' height='100%' fill='{fill_color}' fill-opacity='{fill_opacity}' stroke='black' stroke-opacity='{stroke_opacity}' stroke-width='{stroke_width}' />"
            f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='20' fill='black'>{text}</text>"
            "</svg>"
        )

    @class_property
    def empty_content(cls) -> svg_content:
        return cls.content_for("white", "", 1, "0.1", "0.1")

    @class_property
    def error_content(cls) -> svg_content:
        return cls.content_for("firebrick", "Erro")

    @class_property
    def none_content(cls) -> svg_content:
        return cls.content_for("darkgrey", "Falta", stroke_opacity="0.45")


# TODO
# class MetaSepIconConfig(type):
#     @property
#     def none_content(cls):
#         return cls.content_for("darkgrey", "Falta", stroke_opacity="0.45")

# class SepIconConfig(metaclass=MetaSepIconConfig):
#     ext = "svg"
#     folder = "sep_icons"

#     @staticmethod
#     def content_for(color, text, stroke_opacity=None):
#         return f"<svg color='{color}' text='{text}' opacity='{stroke_opacity}'></svg>"


# eof
