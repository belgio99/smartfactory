from Crypto.Random import get_random_bytes
from crypto_lib import store_aes_key_in_vault, create_client
from vault_lib import start_vault, stop_vault

def main():    
    #try:      
        # Run vault enviroment
        start_vault(True) 

        #create client to comunicate with vault
        client = create_client()

        #create an aes key and store it in Vault
        aes_key = get_random_bytes(32)  # 256-bit AES key
        store_aes_key_in_vault(client,aes_key)
        print("Key stored succesfully.")

    #finally:
        #stop_vault()

if __name__ == "__main__":  
    main()