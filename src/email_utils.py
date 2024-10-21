# src/email_utils.py

import smtplib
from email.message import EmailMessage

# Global email parameters (should be configured)
orig_email = 'PS_extract@gmail.com'
mail_serv = 'smtp.gmail.com'
mail_port = 465
mail_login = ''
mail_passwd = ''

def email_steps(trip_data, steps_info, dest_email, interactive=False):
    """
    Sends emails for each step.
    """
    # Implement email sending logic here
    pass

def send_trip_email(trip_data, dest_email):
    """
    Sends a summary email for the trip.
    """
    # Implement trip email sending logic here
    pass
