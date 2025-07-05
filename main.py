
import asyncio
from telegram_monitor import client, parse_message, group_ids
from solana_trade import buy_token, sell_token, manage_trade
from risk_management import validate_token, check_honeypot, handle_slippage_retry
from logging_utils import log_trade, send_telegram_log
import json

async def main():
    print("Starting bot...")

    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)

    # Start Telegram client
    await client.start(phone=config["telegram"]["phone"])
    print("Telegram client started. Listening for messages...")

    @client.on(events.NewMessage(chats=group_ids))
    async def handler(event):
        if event.message.text:
            print(f"[Main] New message: {event.message.text}")
            tokens = await parse_message(event.message.text)
            if tokens:
                for token_address in tokens:
                    if validate_token(token_address) and not check_honeypot(token_address):
                        print(f"[Main] Valid token found: {token_address}. Attempting to buy.")
                        # Simulate buy
                        tx_hash = await handle_slippage_retry(buy_token, token_address, config["solana"]["max_buy_amount"], config["solana"]["slippage"])
                        if tx_hash:
                            log_trade("BUY", datetime.now().isoformat(), tx_hash)
                            await send_telegram_log(f"Bought {token_address}. Tx: {tx_hash}")
                            # In a real scenario, you'd get the actual buy price here
                            await manage_trade(token_address, initial_buy_price=1.0) # Placeholder initial price
                        else:
                            print(f"[Main] Failed to buy {token_address}")
                    else:
                        print(f"[Main] Token {token_address} failed validation or is a honeypot.")

    await client.run_until_disconnected()

if __name__ == '__main__':
    from datetime import datetime
    asyncio.run(main())


