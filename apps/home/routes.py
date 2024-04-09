# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""


import os

# from app import app
from flask import render_template, url_for
from apps.home.texts import get_text, get_row
from apps.home import blueprint, logHelper, htmlHelper

log = logHelper.Log2Database()


# ============= Index ============== #
@blueprint.route("/index")
# @login_required não pode ter, index é 'livre', depende do menu
def index():
    return render_template("home/index.html", pageTitle="Home")


# ============= Documents ============== #
@blueprint.route("/docs/<docName>")
def docs(docName):
    group = docName
    images, title = get_row("images", group)
    body = "" if (title == "") else get_text("body", group)

    if (title == "") or (body == ""):
        # TODO text:
        body = f"<h4>O documento '{docName}' não foi localizado.</h4>"
        style = ""
        title = "Exibir Documento"
    else:
        images = "image4.png"
        img_path = os.path.join("..", "static", "docs", docName, "img")
        if images != "":
            os.makedirs(img_path, exist_ok=True)
            # TODO Create images

        body = htmlHelper.change_img_paths(body, img_path)
        style = get_text("style", group)

    return render_template(
        "./home/document.html.j2",
        **{
            "pageTitle": "Documento",
            "formTitle": title,
            "documentStyle": style,
            "documentBody": body,
        },
    )
