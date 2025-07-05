
from telethon import TelegramClient, events
import re
import json

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
phone = config['telegram']['phone']
group_ids = config['telegram']['group_ids']

client = TelegramClient('anon', api_id, api_hash)

async def parse_message(message):
    # Regex to detect token callouts (CA:, mint:, or Solana Token Address)
    # This is a basic example and might need refinement
    token_patterns = [
        r'(?:CA:|mint:)\s*([a-zA-Z0-9]{32,44})',  # CA: or mint: followed by address
        r'\b([a-zA-Z0-9]{32,44})\b'  # Standalone Solana address (32-44 alphanumeric characters)
    ]
    
    found_tokens = []
    for pattern in token_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        found_tokens.extend(matches)

    # Filter messages with keywords
    keywords = ['buy', 'new coin', 'pump', 'alpha']
    if any(keyword in message.lower() for keyword in keywords):
        print(f"[Telegram] Detected potential coin call: {message}")
        if found_tokens:
            print(f"[Telegram] Found tokens: {found_tokens}")
            # Here you would pass the token to the trading logic
            return found_tokens
    return []

@client.on(events.NewMessage(chats=group_ids))
async def my_event_handler(event):
    print(f"[Telegram] New message from {event.chat.title if event.chat else 'unknown'}: {event.message.text}")
    if event.message.text:
        await parse_message(event.message.text)

async def main():
    await client.start(phone=phone)
    print("Telegram client started. Listening for messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


