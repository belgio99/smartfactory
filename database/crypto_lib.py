from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import struct
import pandas as pd
from vault_lib import start_vault, stop_vault, create_client

KEY_NAME = "druid-key"

# Define the Vault path where you will store the AES key
vault_path = "my-aes-key"

def store_aes_key_in_vault(vault_client, key: bytes):
    """
    Store the AES key securely in Vault.
    
    Args:
        vault_client: client for Vault
        key (bytes): AES encryption key.
    """
    vault_client.secrets.kv.v2.create_or_update_secret(
        mount_point="secret",
        path=vault_path,
        secret={"aes_key": key.hex()}  # Store the key as a hex string
    )
    print("AES key stored in Vault.")

def retrieve_aes_key_from_vault() -> bytes:
    """
    Retrieve the AES key from Vault.
    
    Returns:
        bytes: The AES encryption key.
    """
    # Start Vault Server
    #start_vault()

    # Create client to comunicate with Vault
    vault_client = create_client()
    secret = vault_client.secrets.kv.v2.read_secret_version(path=vault_path)
    aes_key_hex = secret['data']['data']['aes_key']

    # Stop Vault Server
    #stop_vault()

    return bytes.fromhex(aes_key_hex)  # Convert the hex string back to bytes


def aes_encrypt(data: bytes, key: bytes = None) -> tuple:
    """
    Encrypt data using AES CBC mode.

    Args:
        data (bytes): The data to be encrypted.
        key (bytes, optional): The AES encryption key. If None, a new key will be generated.

    Returns:
        tuple: (encrypted_data, iv, key) where:
            - encrypted_data is the AES encrypted data.
            - iv is the initialization vector used in encryption.
            - key is the AES encryption key used.
    """
    # Convert different types of data to bytes
    if isinstance(data, int):
        # Convert int to bytes (using struct to represent int in 4 bytes)
        data_bytes = struct.pack('i', data)  # 'i' for integer (4 bytes)
    elif isinstance(data, float):
        # Convert float to bytes (using struct to represent float in 8 bytes)
        data_bytes = struct.pack('d', data)  # 'd' for double (8 bytes)
    elif isinstance(data, str):
        # Convert string to bytes (UTF-8 encoding)
        data_bytes = data.encode('utf-8')
    else:
        raise ValueError("Unsupported data type")

    # Create AES cipher object with CBC mode
    cipher = AES.new(key, AES.MODE_CBC)

    # Pad data to match AES block size (16 bytes)
    padded_data = pad(data_bytes, AES.block_size)

    # Encrypt data
    encrypted_data = cipher.encrypt(padded_data)

    # Return encrypted data, IV, and key
    return encrypted_data, cipher.iv, key

def aes_decrypt(encrypted_data: bytes, iv: bytes, data_type: type) -> any:
    """
    Decrypt data using AES with the AES key managed by Vault and convert it back to the original type.
    
    Args:
        encrypted_data (bytes): The encrypted data to be decrypted.
        iv (bytes): The initialization vector used for encryption.
        data_type (type): The type to which the decrypted data should be converted (int, float, str).
        
    Returns:
        any: The decrypted data converted back to the original type.
    """
    # Retrieve the AES key from Vault
    key = retrieve_aes_key_from_vault()

    # Decrypt the data and remove padding
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    # Convert bytes back to the original data type
    if data_type == int:
        return struct.unpack('i', decrypted_data)[0]
    elif data_type == float:
        return struct.unpack('d', decrypted_data)[0]
    elif data_type == str:
        return decrypted_data.decode('utf-8')
    else:
        raise ValueError("Unsupported data type")

def encrypt_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)            
    # Encrypt columns that need protection (we should decide which ones)
    key = retrieve_aes_key_from_vault()
    for column in ["kpi","avg","min","max"]:
        print(f"Processing column: {column} in file: {csv_file_path}")
        df[column]=df[column].apply(aes_encrypt, args=(key,))
    return df