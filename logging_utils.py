
import logging
import os
from datetime import datetime

# Configure file logging
log_file = os.path.join(os.path.dirname(__file__), 'trades.log')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def log_trade(trade_type, timestamp, tx_hash, profit_loss=None):
    message = f"Trade Type: {trade_type}, Timestamp: {timestamp}, Tx Hash: {tx_hash}"
    if profit_loss is not None:
        message += f", P/L: {profit_loss:.2f}%"
    logging.info(message)

# Placeholder for Telegram DM/Discord logging
async def send_telegram_log(message):
    # This would integrate with the Telegram client to send a DM
    print(f"[Telegram Log] {message}")
    pass



