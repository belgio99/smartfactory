import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from database.connection import query_db, get_db_connection
import json

logging.basicConfig(level=logging.INFO)

def send_email(to_email, title, text):
    """
    Sends an email with the specified title and text to the given recipient email address.

    Args:
        to_email (str): The recipient's email address.
        title (str): The subject of the email.
        text (str): The body text of the email.

    Raises:
        Exception: If there is an error sending the email, an exception is logged.
    """
    
    from_email = os.getenv('SMTP_EMAIL')
    from_password = os.getenv('SMTP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = title
    msg.attach(MIMEText(text, 'plain'))

    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.login(from_email, from_password)
        logging.info("Sending email")
        server.send_message(msg)
        server.quit()
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error("Error sending email: " + str(e))
        server.quit()
        raise e

def save_alert(alert):
    """
    Save an alert to the database.

    Args:
        alert (Alert): An instance of the Alert class containing the alert details.

    Raises:
        Exception: If there is an error inserting the alert into the database.

    The alert object should have the following attributes:
        - alertId (str): Unique identifier for the alert.
        - title (str): Title of the alert.
        - type (str): Type of the alert.
        - description (str): Description of the alert.
        - triggeredAt (datetime): Timestamp when the alert was triggered.
        - machineName (str): Name of the machine that triggered the alert.
        - isPush (bool): Whether the alert is a push notification.
        - recipients (list): List of recipients for the alert.
        - severity (Severity): Severity level of the alert.
    """
    query = """
    INSERT INTO Alerts (AlertID, Title, Type, Description, TriggeredAt, MachineName, isPush, Recipients, Severity)
    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
    """.format(
        alert.alertId,
        alert.title,
        alert.type,
        alert.description,
        alert.triggeredAt,
        alert.machineName,
        1 if alert.isPush else 0,
        json.dumps(alert.recipients),
        alert.severity.value
    )

    logging.info("Inserting alert into database")
    try:
        connection, cursor = get_db_connection()
        query_db(cursor, connection, query)
        cursor.close()
        connection.close()
        logging.info("Alert inserted successfully")
    except Exception as e:
        logging.error("Error inserting alert into database: " + str(e))
        raise e    

def send_notification(alert):
    """
    Sends a notification based on the alert type.

    If the alert is a push notification, it logs the action and saves the alert.
    If the alert is an email notification, it sends an email to each recipient listed in the alert.

    Args:
        alert (Alert): An alert object containing notification details. 
                       It should have the following attributes:
                       - isPush (bool): Indicates if the notification is a push notification.
                       - isEmail (bool): Indicates if the notification is an email notification.
                       - recipients (list): A list of email addresses to send the notification to.
                       - notificationTitle (str): The title of the notification.
                       - notificationText (str): The text content of the notification.

    Returns:
        None
    """
    if alert.isPush:
        logging.info("Sending push notification")
        save_alert(alert)
    if alert.isEmail:
        for recipient in alert.recipients:
            logging.info("Sending email to %s", recipient)
            send_email(recipient, alert.notificationTitle, alert.notificationText)

def retrieve_notifications(userId): #TODO - Fix
    query = "SELECT * FROM \"alerts\" WHERE \"recipients\" LIKE '%{}%'".format(userId)
    try:
        connection, cursor = get_db_connection()
        response = query_db(cursor, connection, query)
        cursor.close()
        connection.close()
        return response.json()
    except Exception as e:
        logging.error("Error retrieving alerts for" + userId + ": " + str(e))
        raise e