import requests
from passlib.context import CryptContext
# Constants
API_KEY = "111c50cc-6b03-4c01-9d2f-aac6b661b716"
#BASE_URL = "http://0.0.0.0:10040"
BASE_URL = "https://api-smartfactory.thebelgionas.synology.me"
ENDPOINT = "/smartfactory/register"

# Prompt the user for input
username = input("Enter the username: ")
email = input("Enter the email: ")
password = input("Enter the password: ")
role = input("Enter the role (e.g. FloorFactoryManager): ")
site = input("Enter the site (e.g. site1): ")

# bcrypt
salt = "a"*16 + "e"*6  # 16 'a' + 6 'e'
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = password_context.hash(password, salt=salt)

# Prepare the payload
payload = {
    "username": username,
    "email": email,
    "password": hashed_password,
    "role": role,
    "site": site
}

# Prepare the headers
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# Make the POST request
response = requests.post(BASE_URL + ENDPOINT, json=payload, headers=headers)

# Print response status and body for debugging
print("Status code:", response.status_code)
print("Response body:", response.text)

if response.status_code == 201:
    #Print all payload
    print("Username: ", payload['username'])
    print("Email: ", payload['email'])
    print("Password: ", payload['password'])
    print("Role: ", payload['role'])
    print("Site: ", payload['site'])
    print("User created successfully!")
else:
    print("Failed to create user.")

