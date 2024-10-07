"""
    Email helper, based in sendgrid API


    Equipe da Canoa -- 2024
    mgd
"""

# pylint: disable=E1101
# cSpell:ignore sendgrid Heya

import sendgrid
from os import path
from typing import Callable
from base64 import b64encode

from .ui_texts_helper import get_section
from .py_helper import is_str_none_or_empty, strip_and_ignore_empty

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
    file_to_send_full_name: str = None,
    file_to_send_type: str = None,
) -> bool:
    """» Sends an email, handling both string and dictionary formats for the recipient.

        » Takes the body text from the `vw_ui_texts` (view ui_texts_section) and
          replace it with email_body_params dictionary.

        » Sends an attached file when its path is specified `file_to_send_path`. If extension is is NOT a common
          file type (pdf, json, xlsx, txt, csv), please inform it in `file_to_send_type`

    Args:
        email_to: (str or dict): The recipient information. If a string, it's assumed to be
            the "to" recipient. If a dictionary, it should have keys "to" (optional),
            "cc" (optional), and "bcc" (optional) for the recipient addresses.


    Returns: (mgd 2024-06-05)
        » True if the message was or not `Delivered` (the receiving server accepted the message)
            see https://sendgrid.com/en-us/blog/delivered-bounced-blocked-and-deferred-emails-what-does-it-all-mean
          Otherwise, raises an exception

    Raises:
        TypeError: If the provided email_to is neither a string nor a dictionary.
        ValueError: if the attachment file (file_to_send) has an extension with unknown type.
        RuntimeError: error within the send_mail API
    """
    from ..main import shared

    status_code = 0
    task = ""
    try:
        task = "getting recipients"
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

        task = "checking attachment type"
        ext = (
            None
            if is_str_none_or_empty(file_to_send_full_name)
            or not is_str_none_or_empty(file_to_send_type)
            else path.splitext(file_to_send_full_name)[1].lower()
        )
        if ext is None:
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
            raise ValueError(error)

        task = "preparing body"
        if not is_str_none_or_empty(ui_texts_section):
            texts = get_section(ui_texts_section)
            for key in texts.keys():
                for toReplaceKey in email_body_params.keys():
                    texts[key] = texts[key].replace(
                        "{" + toReplaceKey + "}", email_body_params[toReplaceKey]
                    )

        task = "creating Mail data"
        mail = sendgrid.Mail(
            from_email=shared.app_config.EMAIL_ORIGINATOR,
            to_emails=to_address,
            subject=texts["subject"],
            html_content=texts["content"],
        )

        def _addTo(address: str, fAdd: Callable[[str, str], None]) -> int:
            result = 0
            for item in strip_and_ignore_empty(address, ";"):
                info = strip_and_ignore_empty(item, ',', 2)
                fAdd(info[0] if len(info) == 1 else tuple(info))
                result += 1
            return result

        task = "adding recipients"
        _addTo(cc_address, mail.add_cc)
        _addTo(bcc_address, mail.add_bcc)

        task = "preparing Api"
        apiKey = shared.app_config.EMAIL_API_KEY
        sg = sendgrid.SendGridAPIClient(apiKey)
        if is_str_none_or_empty(file_to_send_full_name):
            pass
        elif not path.exists(file_to_send_full_name):
            raise ValueError(f"File to attach not found [{file_to_send_full_name}].")
        else:
            fileName = path.basename(file_to_send_full_name)
            task = f"reading file [{fileName}]"
            with open(file_to_send_full_name, "rb") as f:
                data = f.read()
            encoded = b64encode(data).decode()
            attachment = sendgrid.Attachment(
                file_content=sendgrid.FileContent(encoded),
                file_type=sendgrid.FileType(file_to_send_type),
                file_name=sendgrid.FileName(fileName),
                disposition=sendgrid.Disposition("attachment"),
            )
            task = f"attaching file [{fileName}]"
            mail.add_attachment(attachment)

        task = f"sending email with subject [{mail.subject}]"

        response = sg.send(mail)
        # https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/responses#status-codes
        status_code = response.status_code
        sent = status_code in [200, 202]  # api docs says 200, but in practice it's 202
        if not sent:
            raise RuntimeError(f"failed with status code {status_code}")

        return sent
    except Exception as e:
        sc = status_code if status_code != 0 else getattr(e, "status_code", 0)
        error = (
            f"Sendgrid email failed while {task}. Error: [{e}], Status Code: [{sc}]."
        )
        msg = getattr(e, "body", str(e))
        msg_error = f"{error} SendGrid: [{msg}]."
        shared.app_log.error(msg_error)
        raise RuntimeError(msg_error)


# eof
