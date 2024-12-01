# FinanceBot  

FinanceBot is a pocket-user Telegram bot designed to help users track their finances effectively. It allows users to manage their budgets, record transactions, and generate reports with ease.  

## Technologies Used  

- **Programming Language**: Python  
- **Telegram Bot Framework**: [aiogram](https://docs.aiogram.dev/)  
- **Database**: SQLite 3, Redis(FSMcontext)

## Setup  

1. Clone the repository:  
   ```bash
   git clone https://github.com/Kurumilog/financebot.git
   cd financebot
   ```  

2. Install required dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  

3. Configure your environment:  
   - Add your Telegram Bot API TOKEN(use this name for variable) to a `.env` file or directly into `bot.py`.  

4. Run the bot:  
   ```bash
   python bot.py
   ```  

## Commands  

| Command            | Description                        |     |
| ------------------ | ---------------------------------- | --- |
| `/start`           | Start the bot.                     |     |
| `/register`        | create profile                     |     |
| `/add_transaction` | guess what it is                   |     |
| `/report`          | view incomes and expenses          |     |
| `/maxreport`       | view incomes and expenses + graphs |     |
| `/user_info`       | all info about you in db           |     |

## Future Features  

- Integration with external APIs for currency conversion.  
- Advanced analytics for financial insights.  
- websocket to track your crypto wallets

## Contributing  

Contributions are welcome! Feel free to submit issues and pull requests.  

## License  

This project is licensed under the MIT License.  

---  

### Author  

Created and maintained by [Kurumilog](https://github.com/Kurumilog).  
