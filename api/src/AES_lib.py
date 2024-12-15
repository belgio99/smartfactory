from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

def encrypt_data(data:str, key):
    '''
    
    '''
    cipher = AES.new(key, AES.MODE_ECB) #use this mode 
    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt_data(data:bytes , key):
    '''
    '''
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(base64.b64decode(data.encode('utf-8'))), AES.block_size)
    return decrypted_data.decode('utf-8')