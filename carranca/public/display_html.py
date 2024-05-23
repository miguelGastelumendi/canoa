# Equipe da Canoa -- 2024
# public\password_reset.py
#
# mgd
# cSpell:ignore tmpl sqlalchemy passwordrecovery is_method_get passwordrecovery
"""
    *Display HTM File*
    Reformats an HTML from the DB:
        - header
        - body
        - images
    using `docName` as a section in
    the db.view vw_ui_texts
"""
import os
import base64

from flask import render_template
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.html_helper import img_filenames, img_change_src_path
from ..helpers.texts_helper import get_msg_error, get_text


def _prepare_img_files(html_images: list[str], db_images: list[str], img_path: str, group: str) -> bool:

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


    # ============= Documents ============== #
    # TODO:
    #    1. Move path to ...
    #    1. Only show Public docs if not logged.
    #    2. check if body exists else error


def do_display_html(docName: str):
    section = docName
    pageTitle = get_text("pageTitle", section)
    formTitle = get_text("formTitle", section)
    body = get_text("body", section)
    style = get_text("style", section)
    # a comma separated list of images.ext names available on the db,
    # see below db_images & _prepare_img_files
    images = get_text("images", section)

    db_images = (
        [] if is_str_none_or_empty(images) else [s.strip() for s in images.split(",")]
    )  # list of img names in db

    html_images = (
        [] if is_str_none_or_empty(body) else sorted(img_filenames(body))
    )  # list of img tags in HTML

    # TODO: check if this is the best way to get a path
    # TODO  path_html_docs = path.join(app_config.ROOT_FOLDER, 'html_docs')
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
        # TODO: have a not_found_image.img

    elif _prepare_img_files(html_images, db_images, img_path, section):
        body = img_change_src_path(body, img_path)

    return render_template(
        "./home/document.html.j2",
        **{
            "pageTitle": pageTitle,
            "formTitle": formTitle,
            "documentStyle": style,
            "documentBody": body,
        },
    )
#eof