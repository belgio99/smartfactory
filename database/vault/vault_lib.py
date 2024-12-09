import subprocess
import time
import hvac
import os
import json

## \file
#  \brief A script to manage the HashiCorp Vault server lifecycle and client operations.

vault_process = None

def create_client():
    """
    Create a client for communicating with Vault and authenticate.

    Returns:
        hvac.Client: An authenticated Vault client.

    Raises:
        SystemExit: If authentication with Vault fails.
    """
    client = hvac.Client()
    if not client.is_authenticated():
        print("Vault authentication failed")
        exit(1)
    print("Authentication successful!")
    return client

def start_vault(first_time=False):
    """
    Start the Vault server with persistent storage configuration.

    Args:
        first_time (bool): Whether this is the first time initializing Vault.

    Globals:
        vault_process: Process object for managing the Vault server.

    Raises:
        Exception: If an error occurs while enabling the KV secrets engine.
    """
    os.environ["VAULT_ADDR"] = "http://127.0.0.1:8200"
    print(f"VAULT_ADDR set to {os.environ['VAULT_ADDR']}")

    global vault_process
    print("Starting Vault with persistent storage...")
    vault_process = subprocess.Popen([
        "vault", "server", "-config=config.hcl"
    ], stdout=open("vault.log", "w"), stderr=subprocess.STDOUT)

    time.sleep(10)

    if first_time:
        root_token, unseal_keys = initialize_vault()
    else:
        with open("vault_keys.json", "r") as file:
            init_data = eval(file.read())
            root_token = init_data["root_token"]
            unseal_keys = init_data["unseal_keys_b64"]

    unseal_vault(unseal_keys)

    print(f"Authenticating with Root Token")
    subprocess.run(["vault", "login", root_token], check=True)

    if first_time:
        try:
            subprocess.run(
                ["vault", "secrets", "enable", "-path=secret", "kv-v2"],
                check=True, capture_output=True, text=True
            )
            print("KV v2 secrets engine enabled successfully on 'secret'.")
        except subprocess.CalledProcessError as e:
            print(f"Error enabling KV v2 secrets engine: {e}")
            print(f"Output: {e.output}")
            print(f"Stderr: {e.stderr}")
            raise

    print("Vault is started.")

def initialize_vault():
    """
    Initialize the Vault server and save the root token and unseal keys.

    Returns:
        tuple: A tuple containing the root token and unseal keys.

    Raises:
        subprocess.CalledProcessError: If an error occurs during Vault initialization.
    """
    try:
        print("Initializing Vault...")
        result = subprocess.run([
            "vault", "operator", "init", "-format=json"
        ], capture_output=True, text=True, check=True)
        init_data = json.loads(result.stdout)
        root_token = init_data["root_token"]
        unseal_keys = init_data["unseal_keys_b64"]

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
    """
    Unseal the Vault server using the unseal keys.

    Args:
        unseal_keys (list): A list of unseal keys.
    """
    for key in unseal_keys:
        subprocess.run(["vault", "operator", "unseal", key], check=True)
    print("Vault unsealed.")

def stop_vault():
    """
    Stop the Vault server if it is running.

    Globals:
        vault_process: Process object for managing the Vault server.
    """
    global vault_process
    if vault_process:
        print("Terminating Vault server...")
        vault_process.terminate()
        vault_process.wait()
        vault_process = None
        print("Vault terminated successfully.")
    else:
        print("Vault server isn't running.")
