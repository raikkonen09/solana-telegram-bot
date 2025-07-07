
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import transfer
from solana.rpc.types import TxOpts
import json
import time
import requests
from jup_ag_sdk import Jupiter

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

solana_client = Client("https://api.devnet.solana.com") # Use devnet for testing
jupiter_client = Jupiter(solana_client)

def load_keypair(path):
    with open(path, "r") as f:
        key_data = json.load(f)
    return Keypair.from_secret_key(bytes(key_data))

wallet_keypair = load_keypair(config["solana"]["private_key_path"])

async def get_token_price(token_address):
    # Using Dexscreener API for price fetching
    try:
        response = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_address}")
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        if data and data["pairs"]:
            # Assuming the first pair is the most relevant
            return float(data["pairs"][0]["priceUsd"])
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price from Dexscreener: {e}")
        return None

async def buy_token(token_address, amount, slippage):
    print(f"[Solana] Attempting to buy {amount} SOL worth of {token_address}")
    try:
        # Get quote from Jupiter
        # Assuming we are buying with SOL (So11111111111111111111111111111111111111112)
        # and the token_address is the output mint
        quote = jupiter_client.quote(
            input_mint=PublicKey("So11111111111111111111111111111111111111112"),
            output_mint=PublicKey(token_address),
            amount=int(amount * 10**9), # Convert SOL to lamports
            slippage_bps=int(slippage * 10000) # Convert slippage to basis points
        )

        if not quote:
            print("[Solana] No quote found for the trade.")
            return None

        # Get swap transaction
        swap_transaction = jupiter_client.swap(
            quote_response=quote,
            user_public_key=wallet_keypair.public_key
        )

        # Deserialize and sign the transaction
        transaction = Transaction.deserialize(swap_transaction.swap_transaction)
        transaction.sign(wallet_keypair)

        # Send the transaction
        resp = solana_client.send_transaction(transaction, wallet_keypair, opts=TxOpts(skip_preflight=True))
        tx_hash = resp["result"]
        print(f"[Solana] Buy order sent. Tx Hash: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"[Solana] Error during buy: {e}")
        return None

async def sell_token(token_address, amount, profit_loss):
    print(f"[Solana] Attempting to sell {amount} of {token_address} with P/L: {profit_loss*100:.2f}%")
    try:
        # Get quote from Jupiter for selling (input is token_address, output is SOL)
        quote = jupiter_client.quote(
            input_mint=PublicKey(token_address),
            output_mint=PublicKey("So11111111111111111111111111111111111111112"),
            amount=int(amount * 10**9), # Assuming amount is in token\"s smallest unit
            slippage_bps=int(config["solana"]["slippage"] * 10000)
        )

        if not quote:
            print("[Solana] No quote found for the sell trade.")
            return None

        # Get swap transaction
        swap_transaction = jupiter_client.swap(
            quote_response=quote,
            user_public_key=wallet_keypair.public_key
        )

        # Deserialize and sign the transaction
        transaction = Transaction.deserialize(swap_transaction.swap_transaction)
        transaction.sign(wallet_keypair)

        # Send the transaction
        resp = solana_client.send_transaction(transaction, wallet_keypair, opts=TxOpts(skip_preflight=True))
        tx_hash = resp["result"]
        print(f"[Solana] Sell order sent. Tx Hash: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"[Solana] Error during sell: {e}")
        return None

async def manage_trade(token_address, initial_buy_price):
    print(f"[Solana] Managing trade for {token_address}. Initial price: {initial_buy_price}")
    
    take_profit_targets = config["trade_logic"]["take_profit"]
    stop_loss_target = config["trade_logic"]["stop_loss"]
    trailing_stop_enabled = config["trade_logic"]["trailing_stop"]

    current_price = await get_token_price(token_address)
    if not current_price:
        print(f"[Solana] Could not fetch current price for {token_address}. Skipping trade management.")
        return

    profit_loss_percentage = (current_price - initial_buy_price) / initial_buy_price

    if profit_loss_percentage >= take_profit_targets[1]: # Check for 100% TP
        print(f"[Solana] Take Profit (100%) triggered for {token_address}")
        await sell_token(token_address, config["solana"]["max_buy_amount"], profit_loss_percentage)
    elif profit_loss_percentage >= take_profit_targets[0]: # Check for 50% TP
        print(f"[Solana] Take Profit (50%) triggered for {token_address}")
        await sell_token(token_address, config["solana"]["max_buy_amount"] / 2, profit_loss_percentage) # Sell half
    elif profit_loss_percentage <= stop_loss_target: # Check for Stop Loss
        print(f"[Solana] Stop Loss triggered for {token_address}")
        await sell_token(token_address, config["solana"]["max_buy_amount"], profit_loss_percentage)
    elif trailing_stop_enabled: 
        # Basic Trailing Stop Logic (needs more sophisticated implementation for production)
        # This example assumes a fixed trailing percentage below the highest price achieved.
        # In a real scenario, you'd store the highest price and continuously update it.
        trailing_percentage = 0.05 # Example: 5% trailing stop
        highest_price = initial_buy_price * 1.5 # Placeholder for highest price achieved

        if current_price <= highest_price * (1 - trailing_percentage):
            print(f"[Solana] Trailing Stop triggered for {token_address}")
            await sell_token(token_address, config["solana"]["max_buy_amount"], profit_loss_percentage)
        else:
            print(f"[Solana] Trailing stop active for {token_address}. Current price: {current_price}, Highest price: {highest_price}")
        pass
    else:
        print(f"[Solana] No trade action for {token_address} at current price.")


async def auto_snipe(token_address, amount, slippage):
    print(f"[Solana] Auto-sniping {amount} of {token_address} with slippage {slippage}")
    return await buy_token(token_address, amount, slippage)


