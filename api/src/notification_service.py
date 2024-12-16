import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from database.connection import query_db, get_db_connection
import json
from model.alert import Alert

logging.basicConfig(level=logging.INFO)

email_subject = "{} - Alert: {}"

email_body = """
Hello,
an alert was geenrated with the following details:

Alert ID: {}
Description: {}
Triggered at: {}
Machine Name: {}
Severity: {}
"""

def send_email(to_email, alert):
    """
    Sends an email notification with the given alert details.

    Args:
        to_email (str): The recipient's email address.
        alert (Alert): An alert object containing details about the alert.

    Raises:
        Exception: If there is an error sending the email.
    """
    from_email = os.getenv('SMTP_EMAIL')
    from_password = os.getenv('SMTP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = email_subject.format(alert.severity.value.upper(), alert.title)
    body = email_body.format(alert.alertId, alert.description, alert.triggeredAt, alert.machineName, alert.severity.value)
    msg.attach(MIMEText(body, 'plain'))

    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.login(from_email, from_password)
        logging.info("Sending email")
        server.send_message(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error("Error sending email: " + str(e))
        raise e
    finally:
        server.quit()

def send_report(to_email, report_name, tmp_path):
    """
    Sends an email notification with the given report pdf file attached.

    Args:
        to_email (str): The recipient's email address.
        report_name (str): The name of the report.
        tmp_path (str): the file path on the server.

    Raises:
        Exception: If there is an error sending the email.
    """
    from_email = os.getenv('SMTP_EMAIL')
    from_password = os.getenv('SMTP_PASSWORD')

    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Report: "+report_name
    msg.set_content("Hello, please find attached your scheduled report")

    try:
        with open(tmp_path, "rb") as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=report_name+".pdf")

        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.login(from_email, from_password)
        logging.info("Sending email")
        server.send_message(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error("Error sending email: " + str(e))
        raise e
    finally:
        server.quit()

def save_alert(alert):
    """
    Save an alert to the database.

    Args:
        alert (Alert): An instance of the Alert class containing the alert details.

    Raises:
        Exception: If there is an error inserting the alert into the database.

    Returns:
        int: The ID of the alert that was inserted.

    The alert object should have the following attributes:
        - title (str): Title of the alert.
        - type (str): Type of the alert.
        - description (str): Description of the alert.
        - triggeredAt (datetime): Timestamp when the alert was triggered.
        - machineName (str): Name of the machine that triggered the alert.
        - isPush (bool): Whether the alert is a push notification.
        - severity (Severity): Severity level of the alert.
    """
    try:
        logging.info("Inserting alert into database")
        connection, cursor = get_db_connection()

        insertAlertQuery = """
        INSERT INTO Alerts (Title, Type, Description, TriggeredAt, MachineName, isPush, Severity)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING AlertID
        """

        cursor.execute(insertAlertQuery, (
            alert.title,
            alert.type,
            alert.description,
            alert.triggeredAt,
            alert.machineName,
            True if alert.isPush else False,
            alert.severity.value
        ))

        alertId = cursor.fetchone()[0]
        logging.info("Alert inserted with ID: %s", alertId)

        logging.info("Retrieving user IDs for recipients")
        select_users_query = """
        SELECT UserID FROM Users WHERE Role = ANY(%s)
        """
        cursor.execute(select_users_query, (alert.recipients,))
        user_ids = cursor.fetchall()

        logging.info("Inserting into association table")
        insert_recipient_query = """
        INSERT INTO AlertRecipients (AlertID, UserID) VALUES (%s, %s)
        """
        for user_id in user_ids:
            cursor.execute(insert_recipient_query, (alertId, user_id[0]))

        connection.commit()
        logging.info("Alert inserted successfully")

        return alertId
    except Exception as e:
        logging.error("Error inserting alert into database: " + str(e))
        raise e    
    finally:
        cursor.close()
        connection.close()

def send_notification(alert):
    """
    Sends a notification based on the alert type.

    If the alert is a push notification, it logs the action and saves the alert.
    If the alert is an email notification, it sends an email to each recipient listed in the alert.

    Args:
        alert (Alert): An alert object containing notification details. 
                       It should have the following attributes:
                       - title (str): Title of the alert.
                        - type (str): Type of the alert.
                        - description (str): Description of the alert.
                        - triggeredAt (datetime): Timestamp when the alert was triggered.
                        - machineName (str): Name of the machine that triggered the alert.
                        - isPush (bool): Whether the alert is a push notification.
                        - severity (Severity): Severity level of the alert.

    Returns:
        None
    """
    if alert.isPush:
        logging.info("Sending push notification")
        alertId = save_alert(alert)
        alert.alertId = alertId
    if alert.isEmail:
        for recipient in alert.recipients:
            emails = retrieve_email(recipient)
            logging.info("Sending email to %s", emails)
            for email in emails:
                send_email(email, alert)

def retrieve_email(role):
    """
    Retrieve email addresses of users with a specific role from the database.

    Args:
        role (str): The role of the users whose email addresses are to be retrieved.

    Returns:
        list: A list of email addresses of users with the specified role.

    Raises:
        Exception: If there is an error retrieving email addresses from the database.
    """
    query = "SELECT Email FROM Users WHERE Role = %s"

    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, (role,))
        response = cursor.fetchall()
        emails = [row[0] for row in response]
        return emails
    except Exception as e:
        logging.error("Error retrieving emails for role " + role + ": " + str(e))
        raise e
    finally:
        cursor.close()
        connection.close()

def retrieve_alerts(userId, all):
    """
    Retrieve alerts for a specific user from the database.
    
    Args:
        userId (str): The ID of the user for whom to retrieve alerts.
        all (bool): Flag to determine whether to retrieve all alerts or only unread alerts.
        
    Returns:
        list: A list of dictionaries, each representing an alert.
        
    Raises:
        Exception: If there is an error retrieving alerts from the database.
    """
    query = """
    SELECT a.* FROM Alerts a
    JOIN AlertRecipients ar ON a.AlertID = ar.AlertID
    JOIN Users u ON ar.UserID = u.UserID
    WHERE u.userID = %s
    """
    
    if not all:
        query += " AND ar.Read = FALSE"

    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, (userId,))
        response = cursor.fetchall()
        
        alerts = []
        for row in response:
            logging.info("Row: %s", row)
            alert = Alert(
                alertId=row[0],
                title=row[1],
                type=row[2],
                description=row[3],
                triggeredAt=str(row[4]),
                machineName=row[5],
                isPush=bool(row[6]),
                isEmail=False,
                recipients=[],
                severity=row[7]
            )
            alerts.append(alert.to_dict())

        # Update all alerts to mark them as read
        update_query = """
        UPDATE AlertRecipients
        SET Read = TRUE
        WHERE UserID = %s
        """
        cursor.execute(update_query, (userId,))
        connection.commit()

        return alerts
    except Exception as e:
        logging.error("Error retrieving alerts for " + userId + ": " + str(e))
        raise e
    finally:
        cursor.close()
        connection.close()