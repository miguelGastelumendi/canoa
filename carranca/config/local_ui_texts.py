"""
local_ui_texts.py

A dictionary of texts for the user interface in
case the database connection fails

Equipe Canoa -- 2025

mgd 2025-03-15
"""

# cSpell:ignore Situación

from ..helpers.html_helper import icon_url
from ..helpers.ui_db_texts_helper import ui_texts_locale, UITextsKeys

default_locale = "en"
default_section = "Form"


class Locale:
    br = "pt-br"
    en = "en"
    es = "es"


local_texts = {
    Locale.br: {
        default_section: {
            UITextsKeys.Form.title: "Situação Inesperada",
            UITextsKeys.Form.date_format: "pt-br",
            UITextsKeys.Form.icon_url: "ups_handler.svg",
        },
        UITextsKeys.Fatal.no_db_conn: {
            UITextsKeys.Msg.warn: "Houve um erro e não foi possível conectar ao banco de dados. Por favor, tente novamente mais tarde."
        },
    },
    Locale.en: {
        default_section: {
            UITextsKeys.Form.title: "Unexpected Situation",
            UITextsKeys.Form.date_format: "en",
            UITextsKeys.Form.icon_url: "ups_handler.svg",
        },
        UITextsKeys.Fatal.no_db_conn: {
            UITextsKeys.Msg.warn: "There was an error and it was not possible to connect to the database. Please try again later."
        },
    },
    Locale.es: {
        default_section: {
            UITextsKeys.Form.title: "Situación Inesperada",
            UITextsKeys.Form.date_format: "es",
            UITextsKeys.Form.icon_url: "ups_handler.svg",
        },
        UITextsKeys.Fatal.no_db_conn: {
            UITextsKeys.Msg.warn: "Hubo un error y no fue posible conectarse a la base de datos. Por favor, inténtelo de nuevo más tarde."
        },
    },
}


def local_ui_texts(section):
    locale = ui_texts_locale()
    ui_texts = local_texts.get(locale, {}).get(section, {})

    if not ui_texts:
        ui_texts = local_texts.get(default_locale, {}).get(section, {})

    return ui_texts


def local_form_texts():
    locale = ui_texts_locale()
    ui_form_texts = local_texts.get(locale, {}).get(default_section, {})
    icon = ui_form_texts[UITextsKeys.Form.icon_url]
    ui_form_texts[UITextsKeys.Form.icon_url] = icon_url("home", icon)

    return ui_form_texts


# eof
