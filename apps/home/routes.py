# -*- encoding: utf-8 -*-
"""
 The Caatinga Team

 mgd 2024-04-09
"""


import os
import base64
from flask import render_template

from apps.home.pyHelper import is_str_none_or_empty
from apps.home.texts import get_msg_error, get_text
from apps.home import blueprint, logHelper, htmlHelper

log = logHelper.Log2Database()


# ============= private ============= #
def _prepare_files(
    html_images: list[str], db_images: list[str], img_path: str, group: str
) -> bool:

    img_path_ready = os.path.exists(img_path)
    missing_files = html_images.copy()  # missing files from folder, assume all

    for file_name in html_images:
        if img_path_ready and os.path.exists(os.path.join(img_path, file_name)):
            missing_files.remove(file_name)  # this is not missing.

    # folder for images & a list of missing_files, ready.
    # available_files are files that are not on the file,
    #   but can be retrieved from the DB (db_images)
    available_files = [file for file in missing_files if file in db_images]
    if missing_files.count == 0:
        return False  # every file in file system

    elif available_files.count == 0:
        return False  # TODO: log this # missing files and no db files to fix

    for file in available_files:
        try:
            b64encoded = get_text(file, group)
            if not is_str_none_or_empty(b64encoded):
                image_data = base64.b64decode(b64encoded)
                with open(os.path.join(img_path, file), "wb") as file:
                    file.write(image_data)
        except Exception as e:
            pass  # TODO: log

    return True


# ============= Index ============== #
@blueprint.route("/index")
# @login_required não pode ter, index é 'livre', depende do menu
def index():
    return render_template("home/index.html", pageTitle="Home")


# ============= Documents ============== #
@blueprint.route("/docs/<docName>")
def docs(docName: str):
    group = docName
    images = get_text("images", group)
    pageTitle = get_text("pageTitle", group)
    formTitle = get_text("formTitle", group)
    body = get_text("body", group)

    db_images = (
        [] if is_str_none_or_empty(images) else [s.strip() for s in images.split(",")]
    )
    html_images = (
        [] if is_str_none_or_empty(body) else sorted(htmlHelper.img_filenames(body))
    )  # list of img tag in HTML

    # TODO: check if this is the best way to get a path
    img_path = os.path.join("\\", "static", "docs", docName, "img")
    if is_str_none_or_empty(body):
        msg = get_msg_error("documentNotFound").format(docName)
        body = f"<h4>{msg}</h4>"
        style = ""  # TODO:
        pageTitle = "Exibir Documento"
        formTitle = "Documento"

    elif html_images.count == 0:
        pass  # html has no images

    elif db_images.count == 0:
        pass  # can't help, no images in db

    elif _prepare_files(
        html_images, db_images, img_path, group
    ):  # html has no missing images
        body = htmlHelper.img_change_path(body, img_path)
        style = get_text("style", group)

    return render_template(
        "./home/document.html.j2",
        **{
            "pageTitle": pageTitle,
            "formTitle": formTitle,
            "documentStyle": style,
            "documentBody": body,
        },
    )
