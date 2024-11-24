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
    logging.info("Checking if user is present in the database")
    if verify_user_presence(userId) == False:
        logging.error("User is not present in the database")
        return False
    logging.info("User is present in the database")
    
    query = "UPDATE Users SET UserSettings = %s WHERE UserID = %s"
    values = (json.dumps(settings), userId)

    logging.info("Saving user settings to database")
    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, values)
        connection.commit()
        logging.info("User settings saved successfully")

        return True
    except Exception as e:
        logging.error("Error saving user settings to database: " + str(e))
        raise e
    finally:
        cursor.close()
        connection.close()
    
def retrieve_user_settings(userId):
    """
    Retrieve user settings from the database.

    Args:
        userId (str): The ID of the user for whom to retrieve settings.
    Returns:
        dict: A dictionary containing the user settings.
    """
    query = "SELECT UserSettings FROM Users WHERE UserID = %s"
    values = (userId,)

    logging.info("Retrieving user settings from database")
    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, values)
        settings = cursor.fetchone()

        if settings and settings[0] is not None:
            return json.loads(settings[0])
        else:
            return {}
    except Exception as e:
        logging.error("Error retrieving user settings from database: " + str(e))
        raise e
    finally:
        cursor.close()
        connection.close()
    
def verify_user_presence(userId):
    """
    Verifies if a user is present in the database.

    Args:
        userId (int): The ID of the user to verify.

    Returns:
        bool: True if the user is present, False otherwise.

    Raises:
        Exception: If there is an issue with the database connection or query execution.
    """
    query = "SELECT COUNT(*) FROM Users WHERE UserID = %s"
    values = (userId,)

    try:
        connection, cursor = get_db_connection()
        cursor.execute(query, values)
        result = cursor.fetchone()[0]
        connection.commit()
    except Exception as e:
        logging.error("Error while checking the presence of the user: " + str(e))
        raise e
    finally:
        cursor.close()
        connection.close()

    return result > 0