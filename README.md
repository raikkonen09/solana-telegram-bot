# Solana Telegram Trading Bot

This project is a fast and functional crypto trading bot that automatically executes buy/sell trades based on new coin call messages from specific Telegram groups.

## Features

- **Telegram Integration**: Monitors messages in real-time from selected public or private Telegram groups, extracts token callouts, and filters messages with keywords.
- **Solana Integration**: Auto-snipes tokens via **Jupiter Aggregator** based on token addresses received from Telegram. Uses a directly configured keypair.
- **Trade Logic**: Executes buy orders instantly after a call. Implements auto-sell logic with **Take Profit at 50% and 100%**, Stop Loss at -25%, and **advanced trailing stop**.
- **Risk & Logging**: Validates tokens via **Dexscreener API** before buying. Includes fail-safes to ignore rugs, **robust honeypot checks (using provided API key)**, and **retry on slippage**. Logs all buys/sells with timestamp, transaction hash, and profit/loss percentage.

## Setup Instructions

### Prerequisites

- Python 3.9+

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
        "api_id": 21904562, 
        "api_hash": "f3d8285206487a87af466122968a5f02",
        "phone": "+40745219564",
        "group_ids": [-1002407791519] 
    },
    "solana": {
        "private_key": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64],
        "slippage": 0.01,
        "max_buy_amount": 0.1,
        "gas_limit": 200000
    },
    "trade_logic": {
        "take_profit": [0.50, 1.00],
        "stop_loss": -0.25,
        "trailing_stop": false,
        "honeypot_api_key": "bcc5b40a-7085-4939-812b-fb59ae7f4539"
    },
    "dry_run": true
}
```

- `api_id` and `api_hash`: Your Telegram API ID and API Hash. Obtain these from [my.telegram.org](https://my.telegram.org/).
- `phone`: Your phone number associated with your Telegram account (e.g., `+40745219564`).
- `group_ids`: A list of Telegram group IDs to monitor. You can get a group ID by forwarding a message from the group to [@userinfobot](https://t.me/userinfobot).
- `private_key`: Your Solana wallet private key as a list of integers. **WARNING: Storing your private key directly in `config.json` is not recommended for production environments. Consider using environment variables or a more secure key management solution for real trading.**
- `slippage`: Maximum acceptable price slippage for trades (e.g., 0.01 for 1%).
- `max_buy_amount`: Maximum amount of SOL to spend per buy trade.
- `gas_limit`: Gas limit for Solana transactions.
- `take_profit`: A list of percentage profits at which to automatically sell (e.g., `[0.50, 1.00]` for 50% and 100%).
- `stop_loss`: Percentage loss at which to automatically sell (e.g., -0.25 for 25%).
- `trailing_stop`: Set to `true` to enable trailing stop loss, `false` otherwise.
- `honeypot_api_key`: Your API key for the honeypot checking service.
- `dry_run`: Set to `true` to simulate trades without executing real transactions. Set to `false` for live trading.

## Usage

To start the bot, run:

```bash
python main.py
```

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


