
import requests
import json
import time

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

honeypot_api_key = config["trade_logic"]["honeypot_api_key"]
DRY_RUN = config.get("dry_run", False)

def validate_token(token_address):
    print(f"[Risk Management] Validating token: {token_address} via Dexscreener...")
    if DRY_RUN:
        print("[Risk Management] DRY RUN: Skipping actual Dexscreener validation.")
        return True # Assume valid in dry run
    try:
        response = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_address}")
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        
        if data and data["pairs"]:
            # Check for basic liquidity and trading volume as indicators of a valid token
            for pair in data["pairs"]:
                if float(pair.get("liquidity", {"usd": 0}).get("usd", 0)) > 1000 and float(pair.get("volume", {"h24": 0}).get("h24", 0)) > 100:
                    print(f"[Risk Management] Token {token_address} appears valid (sufficient liquidity and volume).")
                    return True
            print(f"[Risk Management] Token {token_address} found on Dexscreener but lacks sufficient liquidity/volume.")
            return False
        else:
            print(f"[Risk Management] Token {token_address} not found on Dexscreener.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[Risk Management] Error during Dexscreener validation: {e}")
        return False

def check_honeypot(token_address):
    print(f"[Risk Management] Checking for honeypot: {token_address} via Honeypot.is...")
    if DRY_RUN:
        print("[Risk Management] DRY RUN: Skipping actual Honeypot.is check.")
        return False # Assume not a honeypot in dry run
    try:
        headers = {"Authorization": f"Bearer {honeypot_api_key}"}
        # Assuming Honeypot.is API for Solana is something like this. 
        # The actual endpoint might vary based on their documentation.
        response = requests.get(f"https://api.honeypot.is/v2/IsHoneypot?address={token_address}&chain=solana", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Assuming the API returns a \'honeypot\' field (boolean) or similar
        is_honeypot = data.get("honeypot", True) # Default to True if field is missing or API error
        if is_honeypot:
            print(f"[Risk Management] Token {token_address} is a honeypot.")
        else:
            print(f"[Risk Management] Token {token_address} is NOT a honeypot.")
        return is_honeypot
    except requests.exceptions.RequestException as e:
        print(f"[Risk Management] Error during Honeypot.is check: {e}")
        return True # Assume it\'s a honeypot if check fails

def handle_slippage_retry(func, *args, **kwargs):
    retries = 3
    for i in range(retries):
        try:
            result = func(*args, **kwargs)
            if result:
                return result
        except Exception as e:
            print(f"[Risk Management] Attempt {i+1}/{retries} failed: {e}")
            if i < retries - 1:
                time.sleep(2) # Wait for 2 seconds before retrying
            else:
                print(f"[Risk Management] All {retries} attempts failed.")
    return None


