import requests

def execute_druid_query(url, body):
    """
    Executes a SQL query on a Druid instance.
    
    :param url: The Druid SQL endpoint.
    :param body: A dictionary containing the query body.
    :return: The response from the Druid server.
    """
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None