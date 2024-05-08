# pylint: disable=E1101
import base64
import os
from sendgrid import (SendGridAPIClient, Mail, Attachment, FileContent, FileName, FileType, Disposition)
from .textsHelper import get_section
from carranca.config import Config

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

def send_email(toMail: str, textSection: str, toReplace: dict,  file2SendPath: str = None):
    eMailTexts = get_section(textSection)
    for eMailTextsKey in eMailTexts.keys():
        for toReplaceKey in toReplace.keys():
            eMailTexts[eMailTextsKey] = eMailTexts[eMailTextsKey].replace('{' + toReplaceKey + '}',
                toReplace[toReplaceKey])
    message = Mail(
        from_email = Config.email_originator,
        to_emails = toMail,
        subject = eMailTexts['Subject'],
        html_content = eMailTexts['Text'])
    if file2SendPath is not None:
        with open(file2SendPath, 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        fileName = os.path.basename(file2SendPath)
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('Microsoft Excel 2007+')
        attachment.file_name = FileName(fileName)
        attachment.disposition = Disposition('attachment')
        message.attachment = attachment
    try:
        apiKey= os.environ.get('CANOA_EMAIL_API_KEY')  # mgd GIT -> x
        sendgrid_client = SendGridAPIClient(apiKey)
        response = sendgrid_client.send(message)
        return response
    except Exception as e:
        print(e)
