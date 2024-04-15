# -*- encoding: utf-8 -*-
"""
 The Caatinga Team

 mgd 2024-04-09
"""


import os
import base64
from flask import render_template, redirect, url_for

from apps.authentication.util import is_user_logged
from apps.home.pyHelper import is_str_none_or_empty
from apps.home.texts import get_msg_error, get_text
from apps.home import blueprint, logHelper, htmlHelper

log = logHelper.Log2Database()


# ============= private ============= #
def _prepare_img_files(
    html_images: list[str], db_images: list[str], img_path: str, group: str
) -> bool:

    img_path_ready = os.path.exists(img_path)
    missing_files = html_images.copy()  # missing files from folder, assume all

    for file_name in html_images:
        if img_path_ready and os.path.exists(os.path.join(img_path, file_name)):
            missing_files.remove(file_name)  # this img is not missing.

    # folder for images & a list of missing_files, are ready.
    # available_files are files that are not on the file system,
    #   but can be retrieved from the DB (db_images says so)
    available_files = [file for file in missing_files if file in db_images]
    if missing_files.count == 0:
        return True  # every file is in file system!

    elif available_files.count == 0:
        return True  # some files missing, but I can't fix it :-(
        # TODO: log this # missing files and no db files to fix

    for file in available_files:
        try:
            b64encoded = get_text(file, group)
            if not is_str_none_or_empty(b64encoded):
                image_data = base64.b64decode(b64encoded)
                with open(os.path.join(img_path, file), "wb") as file:
                    file.write(image_data)
        except Exception as e:
            pass
            # TODO: log

    return True


# ============= Home =============== #
@blueprint.route("/home")
# @login_required não pode ter, index é 'livre', depende do menu
def home():
    if is_user_logged():
      return redirect(url_for('home_blueprint.index'))
    else:
      return redirect(url_for('authentication_blueprint.login'))


# ============= Index ============== #
@blueprint.route("/index")
# @login_required não pode ter, index é 'livre', depende do menu
def index():
    if is_user_logged():
        return render_template("home/index.html", pageTitle="Index")
    else:
      return redirect(url_for('authentication_blueprint.login'))



# ============= Documents ============== #
@blueprint.route("/docs/<docName>")
def docs(docName: str):
    group = docName
    pageTitle = get_text("pageTitle", group)
    formTitle = get_text("formTitle", group)
    body = get_text("body", group)
    style = get_text("style", group)
    # a comma separated list of images.ext names available on the db,
    # see below db_images & _prepare_img_files
    images = get_text("images", group)

    db_images = (
        [] if is_str_none_or_empty(images) else [s.strip() for s in images.split(",")]
    )  # list of img names in db

    html_images = (
        [] if is_str_none_or_empty(body) else sorted(htmlHelper.img_filenames(body))
    )  # list of img tags in HTML

    # TODO: check if this is the best way to get a path
    img_path = os.path.join("\\", "static", "docs", docName, "img")
    if is_str_none_or_empty(body):
        msg = get_msg_error("documentNotFound").format(docName)
        body = f"<h4>{msg}</h4>"
        style = ""  # TODO:
        pageTitle = "Exibir Documento"
        formTitle = "Documento"

    elif html_images.count == 0:
        pass
        # html has no images

    elif db_images.count == 0:
        pass
        # if any images are missing in the folder,
        # I can't help, no images found in db

    elif _prepare_img_files(html_images, db_images, img_path, group):
        body = htmlHelper.img_change_path(body, img_path)

    return render_template(
        "./home/document.html.j2",
        **{
            "pageTitle": pageTitle,
            "formTitle": formTitle,
            "documentStyle": style,
            "documentBody": body,
        },
    )

# eof