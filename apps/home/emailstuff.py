import requests
import os
# https://docs.sendgrid.com/pt-br/for-developers/sending-email/api-getting-started
# curl --request POST \
# --url https://api.sendgrid.com/v3/mail/send \
# --header 'Authorization: Bearer <<YOUR_API_KEY>>' \
# --header 'Content-Type: application/json' \
# --data '{"personalizations":[{"to":[{"email":"john.doe@example.com","name":"John Doe"}],"subject":"Hello, World!"}],"content": [{"type": "text/plain", "value": "Heya!"}],"from":{"email":"sam.smith@example.com","name":"Sam Smith"},"reply_to":{"email":"sam.smith@example.com","name":"Sam Smith"}}'

EMAIL_API_KEY = os.environ['EMAIL_API_KEY']

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

def sendPwdEmail(destinationParam: str)-> object:
    global destination
    destination = destinationParam
    return requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=json_data)
