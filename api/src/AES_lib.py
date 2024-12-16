from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

def encrypt_data(data:str, key:bytes):
    '''
    Function to encrypt sensible data. 
    It uses ECB mode because we need the same output for the same encryption key (for db).
    
    Args: 
        data (str): string to encrypt
        key (bytes): AES encryption key
    Returns:
        encrypted_data (str): string of encrypted data
    '''
    cipher = AES.new(key, AES.MODE_ECB) #use this mode 
    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt_data(data:str, key:bytes):
    '''
    Function to decrypt sensible data. 
    It uses ECB mode because we need the same output for the same encryption key (for db).

    Args: 
        data (str): string to encrypt
        key (bytes): AES encryption key
    Returns:
        derypted_data (str): string of decrypted data
    '''
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(base64.b64decode(data.encode('utf-8'))), AES.block_size)
    return decrypted_data.decode('utf-8')
