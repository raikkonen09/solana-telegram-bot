# Solana Telegram Trading Bot

This project is a fast and functional crypto trading bot that automatically executes buy/sell trades based on new coin call messages from specific Telegram groups.

## Features

- **Telegram Integration**: Monitors messages in real-time from selected public or private Telegram groups, extracts token callouts, and filters messages with keywords.
- **Solana Integration**: Auto-snipes tokens via Jupiter Aggregator or Raydium (placeholder for now) based on token addresses received from Telegram. Uses Phantom wallet or a connected keypair.
- **Trade Logic**: Executes buy orders instantly after a call. Implements auto-sell logic with Take Profit (+50%), Stop Loss (-25%), and optional trailing stop.
- **Risk & Logging**: Validates tokens via Dexscreener/Jupiter API (placeholder for now) before buying. Includes fail-safes to ignore rugs and flag honeypots. Logs all buys/sells with timestamp, transaction hash, and profit/loss percentage.

## Setup Instructions

### Prerequisites

- Python 3.9+
- Telegram API ID and API Hash
- Solana wallet private key (JSON file)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/raikkonen09/solana-telegram-bot.git
   cd solana-telegram-bot
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Edit the `config.json` file with your Telegram API credentials, Solana wallet details, and trading parameters.

```json
{
    "telegram": {
        "api_id": 1234567, 
        "api_hash": "your_api_hash_here",
        "phone": "+1234567890",
        "group_ids": [-1001234567890] 
    },
    "solana": {
        "private_key_path": "./phantom_wallet.json",
        "slippage": 0.01,
        "max_buy_amount": 0.1,
        "gas_limit": 200000
    },
    "trade_logic": {
        "take_profit": 0.50,
        "stop_loss": -0.25,
        "trailing_stop": false
    }
}
```

- `api_id` and `api_hash`: Obtain these from [my.telegram.org](https://my.telegram.org/).
- `phone`: Your phone number associated with your Telegram account (e.g., `+1234567890`).
- `group_ids`: A list of Telegram group IDs to monitor. You can get a group ID by forwarding a message from the group to [@userinfobot](https://t.me/userinfobot).
- `private_key_path`: Path to your Solana wallet JSON file.
- `slippage`: Maximum acceptable price slippage for trades (e.g., 0.01 for 1%).
- `max_buy_amount`: Maximum amount of SOL to spend per buy trade.
- `gas_limit`: Gas limit for Solana transactions.
- `take_profit`: Percentage profit at which to automatically sell (e.g., 0.50 for 50%).
- `stop_loss`: Percentage loss at which to automatically sell (e.g., -0.25 for 25%).
- `trailing_stop`: Set to `true` to enable trailing stop loss, `false` otherwise.

## Usage

To start the bot, run:

```bash
python main.py
```

*(Note: `main.py` is not yet created, this is a placeholder for future integration of all modules.)*

## Project Structure

- `telegram_monitor.py`: Handles Telegram message monitoring and parsing.
- `solana_trade.py`: Manages Solana blockchain interactions and trade execution.
- `risk_management.py`: Implements token validation and risk control.
- `logging_utils.py`: Provides logging functionalities.
- `config.json`: Configuration file for the bot.
- `README.md`: This file.
- `trades.log`: Log file for trade history.

## Disclaimer

This bot is provided as-is and for educational purposes only. Cryptocurrency trading involves significant risk, and you could lose money. Use at your own risk. The developer is not responsible for any financial losses incurred from using this software.


