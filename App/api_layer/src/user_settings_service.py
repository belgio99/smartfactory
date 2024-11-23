import json
import logging
from database.connection import get_db_connection

def persist_user_settings(userId, settings):
    """
    Persist user settings to the database.

    This function retrieves the past settings for a given user. If past settings exist,
    it updates the settings in the database. If no past settings exist, it inserts new settings
    into the database.

    Args:
        userId (int): The ID of the user whose settings are to be persisted.
        settings (dict): A dictionary containing the user settings to be saved.

    Raises:
        Exception: If there is an error while saving the user settings to the database.
    """
    past_settings = retrieve_user_settings(userId)
    if past_settings:
        query = "UPDATE UserSettings SET Settings = %s WHERE UserID = %s"
        values = (json.dumps(settings), userId)
    else:
        query = "INSERT INTO UserSettings (UserID, Settings) VALUES (%s, %s)"
        values = (userId, json.dumps(settings))

    logging.info("Saving user settings to database")
    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        logging.info("User settings saved successfully")
    except Exception as e:
        logging.error("Error saving user settings to database: " + str(e))
        raise e
    
def retrieve_user_settings(userId):
    """
    Retrieve user settings from the database.

    Args:
        userId (str): The ID of the user for whom to retrieve settings.
    Returns:
        dict: A dictionary containing the user settings.
    """
    query = "SELECT Settings FROM UserSettings WHERE UserID = %s"
    values = (userId,)

    logging.info("Retrieving user settings from database")
    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, values)
        settings = cursor.fetchone()
        cursor.close()
        connection.close()

        if settings:
            return json.loads(settings[0])
        else:
            return {}
    except Exception as e:
        logging.error("Error retrieving user settings from database: " + str(e))
        raise e