import smtplib
from typing import List


import secret_data # no peeking


# constants
PHONE_NUMBER = secret_data.PHONE_NUMBER # format: <your phone number>@<your cell provider's sms gateway>
# e.g. TMobil's sms gateway is tmomail.net

EMAIL_ADDRESS = secret_data.EMAIL_ADDRESS
EMAIL_PASSWORD = secret_data.EMAIL_PASSWORD


def email_links_to_address(keywords: List[str], links: List[str]):
    message_from = EMAIL_ADDRESS
    message_to = PHONE_NUMBER

    message_subject = ''
    for keyword in keywords:
        message_subject = message_subject + keyword + ', '

    message_body = ''
    for link in links:
        message_body = message_body + link + '\n'

    message = f"From: {message_from}\r\nTo: {message_to}\r\nSubject:{message_subject}\n\n" + message_body

    server = smtplib.SMTP("smtp.gmail.com", 587) # I am using android/google
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(message_from, message_to, message)