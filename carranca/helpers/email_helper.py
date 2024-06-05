# pylint: disable=E1101
# cSpell:ignore sendgrid Heya

from os import path
from base64 import b64encode

import sendgrid

from .texts_helper import get_section
from .py_helper import is_str_none_or_empty

# https://docs.sendgrid.com/pt-br/for-developers/sending-email/api-getting-started
# curl --request POST \
# --url https://api.sendgrid.com/v3/mail/send \
# --header 'Authorization: Bearer <<YOUR_API_KEY>>' \
# --header 'Content-Type: application/json' \
# --data '{"personalizations":[{"to":[{"email":"john.doe@example.com","name":"John Doe"}],"subject":"Hello, World!"}],"content": [{"type": "text/plain", "value": "Heya!"}],"from":{"email":"sam.smith@example.com","name":"Sam Smith"},"reply_to":{"email":"sam.smith@example.com","name":"Sam Smith"}}'

# https://stackoverflow.com/questions/40656019/python-sendgrid-send-email-with-pdf-attachment-file


# headers = {
#    'Authorization': f'Bearer {EMAIL_API_KEY}',
#    'Content-Type': 'application/json',
# }
# response = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=json_data)


def send_email(
    email_to: str | dict,
    ui_texts_section: str,
    email_body_params: dict,
    file_to_send_path: str = None,
    file_to_send_type: str = None,
):
    """» Sends an email, handling both string and dictionary formats for the recipient.

        » Takes the body text from the `vw_ui_texts` (view ui_texts_section) and
          replace it with email_body_params dictionary.

        » Sends an attached file when its path is specified `file_to_send_path`. If extension is is NOT a common
          file type (pdf, json, xlsx, txt, csv), please inform it in `file_to_send_type`

    Args:
        email_to: (str or dict): The recipient information. If a string, it's assumed to be
            the "to" recipient. If a dictionary, it should have keys "to" (optional),
            "cc" (optional), and "bcc" (optional) for the recipient addresses.

    Raises:
        TypeError: If the provided email_to is neither a string nor a dictionary.
        ValueError: if the attachment file (file_to_send) has an extension with unknown type.
        RuntimeError: error within the send_mail API
    """

    # TODO: pass as param
    from main import app_config

    # find recipients
    recipients = None
    if isinstance(email_to, str):
        recipients = {"to": email_to}
    elif isinstance(email_to, dict):
        recipients = dict(email_to)
    else:
        error = f"Unknown `email_to` datatype {type(email_to)}, expected is [str|dict]. Cannot send email."
        raise ValueError(error)

    to_address = recipients.get("to", None)
    cc_address = recipients.get("cc", None)
    bcc_address = recipients.get("bcc", None)

    if is_str_none_or_empty(to_address) and not is_str_none_or_empty(cc_address):
        print(
            "Warning: Sending email with only BCC recipient might be rejected by some servers."
        )

    # Check file_to_send_type
    ext = (
        path.splitext(file_to_send_path)[1].lower()
        if is_str_none_or_empty(file_to_send_type)
        else file_to_send_type
    )
    if ext == None:
        pass
    elif ext == ".pdf":
        file_to_send_type = "application/pdf"
    elif ext == ".json":
        file_to_send_type = "application/json"
    elif ext in [".xls", ".xlsx"]:
        file_to_send_type = "Microsoft Excel 2007+"
    elif ext in [".htm", ".html"]:
        file_to_send_type = "text/html"
    elif ext == ".txt":
        file_to_send_type = "text/plain"
    elif ext == ".csv":
        file_to_send_type = "text/csv"
    else:
        error = f"Unknown MIME type for extension [{ext}], cannot send email."
        # log
        if app_config.DEBUG:
            raise ValueError(error)
        return False

    # check texts
    if not is_str_none_or_empty(ui_texts_section):
        texts = get_section(ui_texts_section)
        for key in texts.keys():
            for toReplaceKey in email_body_params.keys():
                texts[key] = texts[key].replace(
                    "{" + toReplaceKey + "}", email_body_params[toReplaceKey]
                )

    try:
        # prepare Mail ob
        mail = sendgrid.Mail(
            from_email=app_config.EMAIL_ORIGINATOR,
            to_emails=to_address,
            subject=texts["subject"],
            html_content=texts["content"],
        )
        if cc_address:
            mail.add_cc(cc_address)

        if bcc_address:
            mail.add_bcc(bcc_address)

        task = ""
        apiKey = app_config.EMAIL_API_KEY
        sg = sendgrid.SendGridAPIClient(apiKey)
        if file_to_send_path is not None:
            fileName = path.basename(file_to_send_path)
            task = f"reading file [{fileName}]."
            with open(file_to_send_path, "rb") as f:
                data = f.read()
            encoded = b64encode(data).decode()
            attachment = sendgrid.Attachment(
                file_content=sendgrid.FileContent(encoded),
                file_type=sendgrid.FileType(file_to_send_type),
                file_name=sendgrid.FileName(fileName),
                disposition=sendgrid.Disposition("attachment"),
            )
            mail.add_attachment(attachment)

        task = f"email with subject [{mail.subject}]."

        response = sg.send(mail)
        # TODO: get response.status_code
        return response
    except Exception as e:
        error = f"Error on sendgrid {task} error [{e}]."
        # app.logger.error(error)
        if app_config.DEBUG:
            raise RuntimeError(error)
        return False


# eof
