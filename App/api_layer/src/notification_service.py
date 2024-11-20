import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from database.connection import get_db_connection, query_db

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

def save_alert(alert): #TODO - To verify when we'll have a more stable version of the database
    """
    Inserts the alert into the Alerts table in the Druid database.

    Parameters:
    alert (Alert): An alert object containing notification details.

    Returns:
    None
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO Alerts (isPush, isEmail, recipients, notificationTitle, notificationText)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            alert.isPush,
            alert.isEmail,
            ','.join(alert.recipients),
            alert.notificationTitle,
            alert.notificationText
        ))
        connection.commit()
        logging.info("Alert inserted into Druid database successfully")
    except Exception as e:
        logging.error("Error inserting alert into Druid database: " + str(e))
        raise e
    finally:
        cursor.close()
        connection.close()

def send_notification(alert):
    """
    Sends a notification based on the alert type.

    Parameters:
    alert (Alert): An alert object containing notification details. The alert object should have the following attributes:
        - isPush (bool): Indicates if a push notification should be sent.
        - isEmail (bool): Indicates if an email notification should be sent.
        - recipients (list): A list of email addresses to send the notification to.
        - notificationTitle (str): The title of the notification.
        - notificationText (str): The text content of the notification.

    Returns:
    None
    """

    if alert.isPush:
        logging.info("Sending push notification")
        #save_alert(alert)
    if alert.isEmail:
        for recipient in alert.recipients:
            logging.info("Sending email to %s", recipient)
            send_email(recipient, alert.notificationTitle, alert.notificationText)

def retrieve_notifications(userId): #TODO - To verify when we'll have a more stable version of the database (select also the alert for the specified user)
    """
    Retrieves the list of notifications for a user from the Druid database.

    Parameters:
    userId (str): The ID of the user to retrieve notifications for.

    Returns:
    List[Notification]: A list of notifications for the user.
    """
    
    query = "SELECT * FROM \"alerts\""
    response = query_db(query)

    return response.json()