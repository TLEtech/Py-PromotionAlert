import smtplib, ssl

# Input sender information
port = 465  # For SSL
username = ''
password = r''
sender_email = ''
receiver_email = ''

def send_promotions(message):
    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(username, password)
        server.sendmail(sender_email, receiver_email, message)
    return
