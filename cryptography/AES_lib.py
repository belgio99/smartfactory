from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

from api.src.model.user import *
from vault_lib import create_client, store_key_in_vault, retrieve_key_from_vault

default_aes_path = "aes-key"
default_aes_name = "aes_key"

def login_encrypt(log:Login)-> tuple:
    """
    Encrypt data using AES GCM mode.

    Args:
        log (Login): The Login object to be encrypted.

    Returns:
        encrypted_log (Login): register object with encrypted attributes
        iv: the initialization vector used for encryption.
    """
    key = retrieve_key_from_vault(default_aes_path, default_aes_name)  
    # Create AES cipher object with GCM mode
    cipher = AES.new(key, AES.MODE_GCM)
    encrypted_data = {}
    for attribute, value in log.model_dump().items():
        if attribute == "user":
            data_bytes = value.encode('utf-8')
            # Pad data to match AES block size (16 bytes)
            padded_data = pad(data_bytes, AES.block_size)
            # Encrypt data
            encrypted_data[attribute] = cipher.encrypt(padded_data)
        else:
            encrypted_data[attribute] = value
    encrypted_log = Login(**encrypted_data)
    # Return encrypted data, IV
    return encrypted_log, cipher.nonce

def register_encrypt(register: Register) -> tuple:
    """
    Encrypt data using AES GCM mode.

    Args:
        register (Register): The Register object to be encrypted.

    Returns:
        encrypted_register (Register): register object with encrypted attributes
        iv: the initialization vector used for encryption.
    """
    key = retrieve_key_from_vault(default_aes_path, default_aes_name)  
    # Create AES cipher object with GCM mode
    cipher = AES.new(key, AES.MODE_GCM)
    encrypted_data = {}
    for attribute, value in register.model_dump().items():
        if attribute is not "password":
            data_bytes = value.encode('utf-8')
            # Pad data to match AES block size (16 bytes)
            padded_data = pad(data_bytes, AES.block_size)
            # Encrypt data
            encrypted_data[attribute] = cipher.encrypt(padded_data)
    encrypted_register = Register(**encrypted_data)
    # Return encrypted data, IV, and key
    return encrypted_register, cipher.nonce

def aes_decrypt(encrypted_register: Register, iv) -> Register:
    """
    Decrypt data using AES with the AES key managed by Vault and convert it back to the original type.
    
    Args:
        encrypted_register (Register): The encrypted Register object to be decrypted.
        iv (bytes): The initialization vector used for encryption.
        
    Returns:
        Register: The decrypted register converted back to the original one.
    """
    # Retrieve the AES key from Vault
    key = retrieve_key_from_vault(default_aes_path, default_aes_name)  
    
    # Decrypt the data and remove padding
    cipher = AES.new(key, AES.MODE_GCM, iv)
    derypted_data = {}
    for attribute, value in encrypted_register.model_dump().items():
        decrypted_value = unpad(cipher.decrypt(value), AES.block_size).decode('utf-8')
        derypted_data[attribute] = decrypted_value
    register = Register(**derypted_data)
    return register

def create_and_store_aes_key():
    '''
    Create a random key for AES encryption and store it in default path of Vault
    '''
    try:
        client = create_client()
        aes_key = get_random_bytes(32)  # 256-bit AES key
        store_key_in_vault(client, aes_key, default_aes_path, default_aes_name)
        print("Encryption key created and stored succesfully")    
    except Exception as e: 
        print("Error during the creation and storage of the key: %s", e)
        raise
    return

def get_aes_key():
    try:
        aes_key = retrieve_key_from_vault(default_aes_path, default_aes_name)  
        print("Encryption key retrieved succesfully") 
    except Exception as e: 
        print("Error while getting the key: %s", e)
        raise
    return aes_key