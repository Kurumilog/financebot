from aiogram import types, Router, F, html
from aiogram.filters import Command, CommandStart
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User, Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import sqlite3
from datetime import datetime
import re
from keyboards.inline_keyboards import categories_keyboard, transaction_type_keyboard
from database.db import add_user


DATABASE_PATH = 'finance_bot.db'

user_private_router = Router()


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_transaction(user_id, amount, description, category, transaction_type):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO UserTransaction (user_id, amount, description, category, transaction_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, amount, description, category, transaction_type, datetime.now()))
    conn.commit()
    conn.close()

def get_user_transactions(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM UserTransaction WHERE user_id = ?', (user_id,))
    transactions = c.fetchall()
    conn.close()
    return transactions


@user_private_router.message(CommandStart())
async def command_start(message: Message):
    await message.answer("Welcome to finance bot. If you are not registrated yet, please enter /register. else you can view list of commands /commands")

@user_private_router.message(Command('commands'))
async def list_commands(message: Message):
    await message.answer("Here's the list: \n /commands - list of commands, \n /user_info - all info about you in db, \n /add_transaction - guess what is it \n /report - view all incomes and expenses in custom period")


class TransactionForm(StatesGroup):
  amount = State()
  category = State()
  custom_category = State()
  transaction_type = State()

def remove_emojis(text):
  emoji_pattern = re.compile(
      pattern = "["
      u"\U0001F600-\U0001F64F"   
      u"\U0001F300-\U0001F5FF"   
      u"\U0001F680-\U0001F6FF"  
      u"\U0001F1E0-\U0001F1FF"   
      u"\U00002600-\U000026FF"  
      u"\U00002700-\U000027BF"  
      "]+",
      flags = re.UNICODE)
  return emoji_pattern.sub(r'', text).strip()

@user_private_router.message(Command('add_transaction'))
async def add_transaction_start(message: types.Message, state: FSMContext):
  await message.answer("Please enter the amount of the transaction:")
  await state.set_state(TransactionForm.amount)

@user_private_router.message(TransactionForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
  text_input = message.text.strip()
  try:
      amount = int(text_input)
  except ValueError:
      try:
          amount = float(text_input)
      except ValueError:
          await message.answer("❗ Please enter a valid amount using numbers only (e.g., 100 or 100.50).")
          return

  await state.update_data(amount=amount)
  await message.answer(
      "Please select the category of the transaction:",
      reply_markup=categories_keyboard()
  )
  await state.set_state(TransactionForm.category)

@user_private_router.message(TransactionForm.category)
async def process_category(message: types.Message, state: FSMContext):
  category = message.text.strip()
  allowed_categories = ['🍔 Food', '🚌 Transport', '🛍️ Shopping', '💡 Utilities', '💼 Salary', '📈 Investment', 'Other']

  if category not in allowed_categories:
      await message.answer("❗ Please select a category from the keyboard.")
      return

  if category == 'Other':
      await message.answer("Please enter the category:")
      await state.set_state(TransactionForm.custom_category)
  else:
      plain_category = remove_emojis(category)
      await state.update_data(category=plain_category)
      await message.answer(
          "Please select the type of transaction:",
          reply_markup=transaction_type_keyboard()
      )
      await state.set_state(TransactionForm.transaction_type)

@user_private_router.message(TransactionForm.custom_category)
async def process_custom_category(message: types.Message, state: FSMContext):
  category = message.text.strip()
  await state.update_data(category=category)
  await message.answer(
      "Please select the type of transaction:",
      reply_markup=transaction_type_keyboard()
  )
  await state.set_state(TransactionForm.transaction_type)

@user_private_router.message(TransactionForm.transaction_type)
async def process_transaction_type(message: types.Message, state: FSMContext):
  transaction_input = message.text.strip()
  if transaction_input in ['💰 Income', 'Income', '💸 Expense', 'Expense']:
      if 'Income' in transaction_input:
          transaction_type = 'income'
      else:
          transaction_type = 'expense'
      await state.update_data(transaction_type=transaction_type)
      data = await state.get_data()
      user_id = message.from_user.id
      amount = data['amount']
      category = data['category']
      created_at = datetime.now().strftime('%Y-%m-%d')  # for sqlite format
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute('''
          INSERT INTO UserTransaction (user_id, amount, category, transaction_type, created_at)
          VALUES (?, ?, ?, ?, ?)
      ''', (user_id, amount, category, transaction_type, created_at))
      conn.commit()
      conn.close()
      await message.answer("✅ Transaction successfully added!", reply_markup=ReplyKeyboardRemove())
      await state.clear()
  else:
      await message.answer("❗ Please select a valid transaction type from the keyboard.")


@user_private_router.message(Command('user_info'))
async def get_user_info(message: Message):
    user_id = message.from_user.id  

    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("SELECT user_id, first_name, budget, balance FROM user WHERE user_id = ?", (user_id,))
        user_data = c.fetchone()

        if user_data:
            user_id, first_name, budget, balance = user_data

            response = (
                f"👤 *User Information*\n\n"
                f"🔑 User ID: `{user_id}`\n"
                f"👤 Name: `{first_name}`\n"
                f"💸 Planned Budget: `{budget:.2f}`\n"
                f"💰 Current Balance: `{balance:.2f}`"
            )
        else:
            response = "❌ Your data is not found in the database. Please register to start using the bot."

    except sqlite3.Error as e:
        response = f"⚠️ Database error: {e}"
    finally:
        if conn:
            conn.close()

    await message.answer(response, parse_mode="Markdown")
    

class ReportForm(StatesGroup):
    start_date = State()
    end_date = State()
    

@user_private_router.message(Command('report'))
async def report_start(message: Message, state: FSMContext):
    await message.answer("📅 Please enter the **start date** for the report (format: DD-MM-YYYY):")
    await state.set_state(ReportForm.start_date)

@user_private_router.message(ReportForm.start_date)
async def process_start_date(message: Message, state: FSMContext):
    start_date_str = message.text.strip()
    try:
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        await state.update_data(start_date=start_date)
        print(start_date)
        await message.answer("📅 Please enter the **end date** for the report (format: DD-MM-YYYY):")
        await state.set_state(ReportForm.end_date)
    except ValueError:
        await message.answer("❗ Invalid date format. Please enter the date in DD-MM-YYYY format.")
    return

@user_private_router.message(ReportForm.end_date)
async def process_end_date(message: Message, state: FSMContext):
    end_date_str = message.text.strip()
    data = await state.get_data()
    start_date = data.get('start_date')

    try:
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y")
        if end_date < start_date:
            await message.answer("❗ End date cannot be earlier than start date. Please enter a valid end date.")
            return
        print(end_date)

        start_date_db = start_date.strftime('%Y-%m-%d')
        end_date_db = end_date.strftime('%Y-%m-%d')

        user_id = message.from_user.id
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
    SELECT transaction_type, SUM(amount) as total_amount
    FROM UserTransaction
    WHERE user_id = ? AND
        DATE(created_at) BETWEEN DATE(?) AND DATE(?)
    GROUP BY transaction_type
''', (user_id, start_date_db, end_date_db))

        results = cursor.fetchall()

        total_income = 0.0
        total_expense = 0.0

        for row in results:
            if row['transaction_type'] == 'income':
                total_income = row['total_amount'] if row['total_amount'] else 0.0
            elif row['transaction_type'] == 'expense':
                total_expense = row['total_amount'] if row['total_amount'] else 0.0

        balance = total_income - total_expense

        start_date_str_formatted = start_date.strftime('%d-%m-%Y')
        end_date_str_formatted = end_date.strftime('%d-%m-%Y')

        report_message = (
            f"📊 **Report from {start_date_str_formatted} to {end_date_str_formatted}**\n\n"
            f"💰 Total Income: {total_income:.2f}\n"
            f"💸 Total Expenses: {total_expense:.2f}\n"
            f"📈 Net Balance: {balance:.2f}"
        )

        await message.answer(report_message, parse_mode='Markdown')
        await state.clear()
        conn.close()
    except ValueError:
        await message.answer("❗ Invalid date format. Please enter the date in DD-MM-YYYY format.")
        return