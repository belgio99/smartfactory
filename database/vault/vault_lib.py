import subprocess
import time
import hvac
import os
import json

vault_process = None

def create_client(): 
    # Creazione del client per comunicare con Vault
    client = hvac.Client()
    # Verifica la connessione a Vault
    if not client.is_authenticated():
        print("Vault authentication failed")
        exit(1)
    print("Autenticazione riuscita!")
    return client

def start_vault(first_time=False):
    # Set Vault's address as an environment variable
    os.environ["VAULT_ADDR"] = "http://127.0.0.1:8200"
    print(f"VAULT_ADDR set to {os.environ['VAULT_ADDR']}")
    
    global vault_process
    # Start Vault with persistent storage configuration
    print("Starting Vault with persistent storage...")
    vault_process = subprocess.Popen(["vault", "server", "-config=config.hcl"],
                                      stdout=open("vault.log", "w"),
                                      stderr=subprocess.STDOUT)
    # Wait for Vault to start
    time.sleep(10)

    if first_time:
        root_token, unseal_keys = initialize_vault()
    else:
        with open("vault_keys.json", "r") as file:
            init_data = eval(file.read())
            root_token = init_data["root_token"]
            unseal_keys = init_data["unseal_keys_b64"]

    # Unseal Vault
    unseal_vault(unseal_keys)

    # Authenticate with the root token
    print(f"Authenticating with Root Token")
    subprocess.run(["vault", "login", root_token], check=True)
    
    if first_time:
        try:
            # Abilita il motore di segreti KV v2
            subprocess.run(
                ["vault", "secrets", "enable", "-path=secret", "kv-v2"],
                check=True,
                capture_output=True,
                text=True
            )
            print("Motore KV v2 abilitato con successo su 'secret'.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'abilitazione del motore KV v2: {e}")
            print(f"Output: {e.output}")
            print(f"Stderr: {e.stderr}")
            raise

    print("Vault is started.")

def initialize_vault():
    try:
        # Initialize Vault if not already initialized
        print("Initializing Vault...")
        result = subprocess.run(["vault", "operator", "init", "-format=json"], capture_output=True, text=True, check=True)
        init_data = json.loads(result.stdout)  # Parsing JSON output
        root_token = init_data["root_token"]
        unseal_keys = init_data["unseal_keys_b64"]

        # Save keys securely (this is for demo purposes only)
        with open("vault_keys.json", "w") as file:
            file.write(result.stdout)
        print("Vault initialized. Root token and unseal keys saved to 'vault_keys.json'.")
        
        return root_token, unseal_keys
    
    except subprocess.CalledProcessError as e:
        print(f"Error initializing Vault: {e}")
        print(f"Command output: {e.output}")
        print(f"Command stderr: {e.stderr}")
        raise

def unseal_vault(unseal_keys):
    # Unseal Vault using the unseal keys
    for key in unseal_keys:
        subprocess.run(["vault", "operator", "unseal", key], check=True)
    print("Vault unsealed.")

def stop_vault():
    global vault_process
    if vault_process:
        print("Terminating Vault server...")
        # Invio del segnale di interruzione al processo Vault
        vault_process.terminate()
        vault_process.wait()  # Attendi che il processo termini
        vault_process = None
        print("Vault terminated succesfully.")
    else:
        print("Vault server isn't running.")

