import subprocess, re
import hvac


def store_key_in_vault(client, key: bytes, vault_path: str, key_name: str) -> None:
    """
    Store the key securely in Vault.
    
    Args:
        vault_client: client for Vault
        key (bytes): AES encryption key.
        path: name of the path to identify the key in Vault
        key_name: name of the key in Vault
    """
    client.secrets.kv.v2.create_or_update_secret(
        path=vault_path,
        secret={key_name: key.hex()}  # Store the key as a hex string
    )
    print("AES key stored in Vault succesully.")

def retrieve_key_from_vault(client, vault_path: str, key_name: str) -> bytes:
    '''
    Retrieve the key stored in Vault
    Args:
        client: Vault client
        vault_path (str): Name of the path to identify the key in Vault
        key_name: name of the key in Vault
    Returns:
        bytes: The retrieved key
    '''
    secret = client.secrets.kv.v2.read_secret_version(path=vault_path, raise_on_deleted_version=True)
    # Extract the key using key_name
    key_hex = secret['data']['data'][key_name]  
    if key_hex is None:
        raise KeyError(f"Key not found in Vault at path '{vault_path}'")
    
    # Convert hex string back to bytes
    return bytes.fromhex(key_hex)

def get_root_token():
    '''
    Method to obtain the Vault root token from the Vault log
    '''
    # Run the Docker logs command to get the logs from the Vault container
    result = subprocess.run(['docker', 'logs', 'vault'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check if the command was successful
    if result.returncode != 0:
        raise Exception(f"Error retrieving logs: {result.stderr.decode()}")
    
    # Search the logs for the root token (it should look like 'Root Token: s.abcdef1234567890')
    log_output = result.stdout.decode()
    match = re.search(r'Root Token:\s*([a-zA-Z0-9.]+)', log_output)
    
    if match:
        return match.group(1)
    else:
        raise Exception("Root token not found in Vault logs")

def create_client(): 
    '''
    Create Client to communicate with Vault
    '''
    client = hvac.Client(url='http://localhost:8200')
    print("client")
    client.token = get_root_token()
    print(client.token)
    # Verifica la connessione a Vault
    if not client.is_authenticated():
        print("Vault authentication failed")
        exit(1)
    print("Autenticazione riuscita!")
    return client


