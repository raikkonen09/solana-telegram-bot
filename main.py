
import asyncio
from telethon import TelegramClient, events
import re
import json
from datetime import datetime

from solana_trade import buy_token, sell_token, manage_trade
from risk_management import validate_token, check_honeypot, handle_slippage_retry
from logging_utils import log_trade, send_telegram_log

async def main():
    print("Starting bot...")

    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)

    # Set DRY_RUN flag from config
    DRY_RUN = config.get("dry_run", False)
    print(f"DRY_RUN mode is set to: {DRY_RUN}")

    # Initialize Telegram client
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    phone = config["telegram"]["phone"]
    group_ids = config["telegram"]["group_ids"]

    client = TelegramClient("anon", api_id, api_hash)

    # Connect to Telegram
    await client.start(phone=phone)
    print("Telegram client started. Listening for messages...")

    @client.on(events.NewMessage(chats=group_ids))
    async def handler(event):
        if event.message.text:
            print(f"[Main] New message: {event.message.text}")
            
            # Regex to detect token callouts (CA:, mint:, or Solana Token Address)
            token_patterns = [
                r"(?:CA:|mint:)\s*([a-zA-Z0-9]{32,44})",  # CA: or mint: followed by address
                r"\b([a-zA-Z0-9]{32,44})\b"  # Standalone Solana address (32-44 alphanumeric characters)
            ]
            
            found_tokens = []
            for pattern in token_patterns:
                matches = re.findall(pattern, event.message.text, re.IGNORECASE)
                found_tokens.extend(matches)

            # Filter messages with keywords
            keywords = ["buy", "new coin", "pump", "alpha"]
            if any(keyword in event.message.text.lower() for keyword in keywords):
                print(f"[Main] Detected potential coin call: {event.message.text}")
                if found_tokens:
                    for token_address in found_tokens:
                        print(f"[Main] Found token: {token_address}")
                        
                        # Validate token and check for honeypot
                        is_valid = validate_token(token_address)
                        is_honeypot = check_honeypot(token_address)

                        if is_valid and not is_honeypot:
                            print(f"[Main] Token {token_address} is valid and not a honeypot. Attempting to buy.")
                            # Simulate buy
                            tx_hash = await handle_slippage_retry(buy_token, token_address, config["solana"]["max_buy_amount"], config["solana"]["slippage"])
                            if tx_hash:
                                log_trade("BUY", datetime.now().isoformat(), tx_hash, token_address, config["solana"]["max_buy_amount"], 0.0) # Price is unknown at buy
                                await send_telegram_log(f"Bought {token_address}. Tx: {tx_hash}")
                                # In a real scenario, you would get the actual buy price here
                                # For dry run, we'll use a mock price for manage_trade
                                await manage_trade(token_address, initial_buy_price=1.0) # Placeholder initial price
                            else:
                                print(f"[Main] Failed to buy {token_address}")
                        else:
                            print(f"[Main] Token {token_address} failed validation or is a honeypot. Skipping trade.")

    # For dry run, send a simulated message after a short delay
    if DRY_RUN:
        await asyncio.sleep(5) # Give some time for Telegram client to connect
        print("[Main] Sending simulated Telegram message for dry run...")
        # Use a known valid Solana token address for simulation
        simulated_message = "New coin call! Buy now! CA: 7d1jXgXy2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a"
        # Create a mock event object
        class MockChat:
            title = "Simulated Group"
        class MockMessage:
            text = simulated_message
        class MockEvent:
            chat = MockChat()
            message = MockMessage()

        await handler(MockEvent()) # Call the handler directly with the mock event
        print("[Main] Simulated message sent. Waiting for 10 seconds to allow processing...")
        await asyncio.sleep(10) # Allow time for the simulated trade to process
        print("[Main] Dry run simulation complete.")
        # Optionally, you can add logic here to print simulated stats from logs
        # For now, the logs will be printed to console during the dry run

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())


