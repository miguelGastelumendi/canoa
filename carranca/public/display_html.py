"""
    *Display HTM File*
    Reformats an HTML from the DB:
        - header
        - body
        - images
    using `docName` as a section in
    the db.view vw_ui_texts

    Equipe da Canoa -- 2024
    mgd
"""

# cSpell:ignore

import os
import base64

from flask import render_template
from ..helpers.file_helper import folder_must_exist
from ..helpers.py_helper import is_str_none_or_empty
from ..helpers.html_helper import img_filenames, img_change_src_path
from ..Sidekick import sidekick


def __prepare_img_files(
    html_images: list[str], db_images: list[str], img_local_path: str, section: str
) -> bool:
    from ..helpers.ui_texts_helper import get_text

    is_img_local_path_ready = os.path.exists(img_local_path)
    missing_files = html_images.copy()  # missing files from folder, assume all

    for file_name in html_images:
        if is_img_local_path_ready and os.path.exists(
            os.path.join(img_local_path, file_name)
        ):
            missing_files.remove(file_name)  # this img is not missing.

    if not folder_must_exist(img_local_path):
        sidekick.app_log.error(
            f"Cannot create folder [{img_local_path}] to keep the HTML's images."
        )
        return False

    # folder for images & a list of missing_files, are ready.
    # available_files are files that are not on the file system,
    #   but can be retrieved from the DB (db_images says so)
    available_files = [file for file in missing_files if file in db_images]
    repairable_files = len(available_files) - len(missing_files)
    if len(missing_files) == 0:
        return True  # every file is in file system!

    elif len(available_files) == 0:
        q = len(missing_files)
        qtd = 'One' if q == 1 else f'{q}'
        p = '' if q == 1 else 's'
        sidekick.app_log.warn(
            f"{qtd} image record{p} missing for [sectorSpecifications] in database: {', '.join(missing_files)}."
        )
        return True  # some files missing, but I can't fix it :-(

    for file in available_files:
        try:
            b64encoded = get_text(file, section)
            if not is_str_none_or_empty(b64encoded):
                image_data = base64.b64decode(b64encoded)
                with open(os.path.join(img_local_path, file), 'wb') as file:
                    file.write(image_data)
        except Exception as e:
            sidekick.app_log.error(
                f'Error writing image [{file}] in folder {img_local_path}. Message [{str(e)}]'
            )

    return True

    # ============= Documents ============== #
    # TODO:
    #    1. Move path to ...
    #    1. Only show Public docs if not logged.
    #    2. check if body exists else error


def display_html(docName: str):
    from ..helpers.ui_texts_helper import get_msg_error, get_text, get_html

    section = docName
    ## TODO texts = get_html( section )
    pageTitle = get_text('pageTitle', section)
    formTitle = get_text('formTitle', section)
    body = get_text('body', section, '')
    style = get_text('style', section, '')
    # a comma separated list of images.ext names available on the db,
    # see below db_images & _prepare_img_files
    images = get_text('images', section)

    db_images = (
        [] if is_str_none_or_empty(images) else [s.strip() for s in images.split(',')]
    )  # list of img names in db

    html_images = (
        [] if is_str_none_or_empty(body) else sorted(img_filenames(body))
    )  # list of img tags in HTML

    img_folders = ['static', 'docs', section, 'images']
    img_local_path = os.path.join(sidekick.config.ROOT_FOLDER, *img_folders)
    if is_str_none_or_empty(body):
        msg = get_msg_error('documentNotFound').format(docName)
        body = f'<h4>{msg}</h4>'
        style = ''  # TODO:
        pageTitle = 'Exibir Documento'
        formTitle = 'Documento'

    elif len(html_images) == 0:
        pass
        # html has no images

    elif len(db_images) == 0:
        pass
        # if any images are missing in the folder,
        # I can't help, no images found in db
        # TODO: have a not_found_image.img

    elif __prepare_img_files(html_images, db_images, img_local_path, section):
        img_folders.insert(0, os.sep)
        body = img_change_src_path(body, img_folders)
        pass

    # DEBUG
    # temp = sidekick.app.jinja_env.from_string( '{{ app_version() }}  + {{ app_name()}}' )
  #  print(temp.render())

    return render_template(
        './home/document.html.j2',
        **{
            'pageTitle': pageTitle,
            'formTitle': formTitle,
            'documentStyle': style,
            'documentBody': body,
        },
    )

# eof
