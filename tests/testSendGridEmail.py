# https://sendgrid.com/blog/sending-emails-from-python-flask-applications-with-twilio-sendgrid/

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    #from_email='refloresta_sp@mail.sigam.sp.gov.br',
    from_email='assismauro@hotmail.com',
    to_emails='assismauro64@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')

EMAIL_API_KEY = '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'

sg = SendGridAPIClient(EMAIL_API_KEY)
response = sg.send(message)
print(response.status_code, response.body, response.headers)
