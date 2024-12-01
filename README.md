# Finance Bot

Finance Bot is a Telegram bot designed to help users manage their finances by tracking transactions, budgets, and balances.

## Features

- User registration and authentication
- Transaction tracking (income and expenses)
- Budget management
- Balance updates
- User information retrieval

## Prerequisites

- Docker
- Docker Compose (optional, for multi-container setups)
- Telegram Bot Token (obtain from [BotFather](https://core.telegram.org/bots#botfather))

## Setup

1. **Clone the repository:**
bash
git clone https://github.com/Kurumilog/financebot.git
cd financebot
2. **Create a `.env` file:**

 Create a `.env` file in the root directory and add your Telegram bot token:
 env
TOKEN=your_telegram_bot_token
3. **Build and run the Docker container:**
bash
docker build -t financebot .
docker run --env-file .env -p 8000:8000 financebot
Alternatively, if using Docker Compose:
bash
docker-compose up --build
4. **Interact with the bot:**

 Open Telegram and start a chat with your bot using the token provided.

## Database

The bot uses SQLite for data storage. The database file `finance_bot.db` is created automatically in the project directory.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
