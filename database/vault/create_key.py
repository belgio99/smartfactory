from Crypto.Random import get_random_bytes
from crypto_lib import store_aes_key_in_vault, create_client
from vault_lib import start_vault, stop_vault

## \file
#  \brief A script to generate an AES key, store it in Vault, and manage the Vault environment.

def main():
    """
    Main function to manage the Vault environment, create an AES key, and store it in Vault.

    Steps:
        1. Start the Vault environment.
        2. Create a client to communicate with Vault.
        3. Generate a 256-bit AES key.
        4. Store the generated AES key in Vault.
        5. Stop the Vault environment (if enabled).

    Raises:
        Exception: If there is an error during any step of the process.
    """
    # Uncomment the try-finally block to ensure the Vault environment is stopped properly
    #try:
        # Run Vault environment
    start_vault(True)

    # Create a client to communicate with Vault
    client = create_client()

    # Generate a 256-bit AES key and store it in Vault
    aes_key = get_random_bytes(32)
    store_aes_key_in_vault(client, aes_key)
    print("Key stored successfully.")

    #finally:
        # Stop the Vault environment
        #stop_vault()

# Entry point
if __name__ == "__main__":
    main()
