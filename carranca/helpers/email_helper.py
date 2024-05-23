# pylint: disable=E1101
#cSpell:ignore sendgrid Heya

from os import path
from base64 import b64encode

from sendgrid import SendGridAPIClient, Mail, Attachment, FileContent, FileName, FileType, Disposition
from main import app_config

from .texts_helper import get_section
from .py_helper import is_str_none_or_empty

# https://docs.sendgrid.com/pt-br/for-developers/sending-email/api-getting-started
# curl --request POST \
# --url https://api.sendgrid.com/v3/mail/send \
# --header 'Authorization: Bearer <<YOUR_API_KEY>>' \
# --header 'Content-Type: application/json' \
# --data '{"personalizations":[{"to":[{"email":"john.doe@example.com","name":"John Doe"}],"subject":"Hello, World!"}],"content": [{"type": "text/plain", "value": "Heya!"}],"from":{"email":"sam.smith@example.com","name":"Sam Smith"},"reply_to":{"email":"sam.smith@example.com","name":"Sam Smith"}}'

# https://stackoverflow.com/questions/40656019/python-sendgrid-send-email-with-pdf-attachment-file


#headers = {
#    'Authorization': f'Bearer {EMAIL_API_KEY}',
#    'Content-Type': 'application/json',
#}
#response = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=json_data)

def send_email(toMail: str, textsSection: str, toReplace: dict, file2SendPath: str = None, file2SendType: str = None):

    ext = path.splitext(file2SendPath)[1].lower()
    if not is_str_none_or_empty(file2SendType):
        pass
    elif ext == '.pdf':
       file2SendType =  "application/pdf"
    elif ext == '.json':
        file2SendType = 'application/json'
    elif ext in ['.xls', '.xlsx']:
        file2SendType = "Microsoft Excel 2007+"
    elif ext in ['.htm', '.html']:
        file2SendType = "text/html"
    elif ext == '.txt' :
        file2SendType = "text/plain"
    elif ext == '.csv':
        file2SendType = "text/csv"
    else:
        error = f"Unknown MIME type for extension [{ext}], cannot send email."
        raise ValueError(error)

    if not is_str_none_or_empty(textsSection):
        texts = get_section(textsSection)
        for key in texts.keys():
            for toReplaceKey in toReplace.keys():
                texts[key] = texts[key].replace('{' + toReplaceKey + '}', toReplace[toReplaceKey])

    message = Mail(
        from_email = app_config.EMAIL_ORIGINATOR,
        to_emails = toMail,
        subject = texts['subject'],
        html_content = texts['content'])

    task = ''
    try:
        if file2SendPath is not None:
            fileName = path.basename(file2SendPath)
            task = f"reading file [{fileName}]."
            with open(file2SendPath, 'rb') as f:
                data = f.read()
            encoded = b64encode(data).decode()
            attachment = Attachment(
                file_content = FileContent(encoded),
                file_type = FileType(file2SendType),
                file_name = FileName(fileName),
                disposition = Disposition('attachment')
            )
            message.attachment = attachment

        task = f"email with subject [{message.subject}]."
        apiKey = app_config.EMAIL_API_KEY
        send_grid_client = SendGridAPIClient(apiKey)
        response = send_grid_client.send(message)
        return response
    except Exception as e:
        error = f"Error on sendGrid {task} error [{e}]."
        #app.logger.error(error)
        if app_config.DEBUG:
            raise RuntimeError(error)
        return False

#eof
