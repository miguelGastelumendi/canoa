import base64

import requests
import os
from sendgrid import (SendGridAPIClient, Mail, Attachment, FileContent,
                      FileName, FileType, Disposition, ContentId)
from .helper import getFormText

# https://docs.sendgrid.com/pt-br/for-developers/sending-email/api-getting-started
# curl --request POST \
# --url https://api.sendgrid.com/v3/mail/send \
# --header 'Authorization: Bearer <<YOUR_API_KEY>>' \
# --header 'Content-Type: application/json' \
# --data '{"personalizations":[{"to":[{"email":"john.doe@example.com","name":"John Doe"}],"subject":"Hello, World!"}],"content": [{"type": "text/plain", "value": "Heya!"}],"from":{"email":"sam.smith@example.com","name":"Sam Smith"},"reply_to":{"email":"sam.smith@example.com","name":"Sam Smith"}}'

# https://stackoverflow.com/questions/40656019/python-sendgrid-send-email-with-pdf-attachment-file
EMAIL_API_KEY = os.environ['EMAIL_API_KEY']

fromEmail = 'refloresta_sp@mail.sigam.sp.gov.br'

headers = {
    'Authorization': f'Bearer {EMAIL_API_KEY}',
    'Content-Type': 'application/json',
}

destination = 'hcarrascosa@sp.gov.br'
name = 'Mauro'
sender = 'refloresta@mail.sigam.sp.gov.br'
subject = "Óia eu aí!!!!"
message = 'Olá, mamãe Juju, aqui é o ReflorestaSP!'

json_data = {
    'personalizations': [
        {
            'to': [
                {
                    'email': f'{destination}',
                    'name': f'{name}',
                },
            ],
            'subject': f'{subject}',
        },
    ],
    'content': [
        {
            'type': 'text/plain',
            'value': f'{message}',
        },
    ],
    'from': {
        'email': f'{sender}',
        'name': 'ReflorestaSP',
    },
    'reply_to': {
        'email': f'{sender}',
        'name': 'ReflorestaSP',
    },
}

#response = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=json_data)

#def sendPwdEmail(destinationParam: str)-> object:
#    global destination
#    destination = destinationParam
#    return requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=json_data)

def sendEmail(toMail: str, file2SendPath: str = None):
    texts = getFormText('emailProjectOutput')
    message = Mail(
    from_email=fromEmail,
    to_emails=toMail,
    subject=texts['Subject'],
    html_content=texts['Text'])
    with open(file2SendPath, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    if file2SendPath is not None:
        fileName = os.path.basename(file2SendPath).split('.')[0]
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        attachment.file_name = FileName(fileName)
        attachment.disposition = Disposition('attachment')
        #attachment.content_id = ContentId('Example Content ID')
        message.attachment = attachment
    try:
        sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)
        return response
    except Exception as e:
        print(e.message)