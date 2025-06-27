import smtplib
from email.message import EmailMessage

email_sender = 'vijayayeditha8537@gmail.com'
email_password = 'vsyw vipa huph rqcz'
email_receiver = 'kondamadugulaalekya@gmail.com'

subject = 'Test Email'
body = 'This is a test.'

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
    print("Sent!")
except Exception as e:
    print("Error:", e)