from aiogram import types, Router, F, html
from aiogram.filters import Command, CommandStart, StateFilter
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User, Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


import sqlite3

#importing keyboards from keyboards/reply_keyboards.py
from keyboards.reply_keyboards import categories_keyboard, transaction_type_keyboard
from keyboards.reply_keyboards import cancel_keyboard

#importing func from database/db.py 
from database.db import add_user
from database.db import get_db_connection

#you can read the descriptin of this func in utils/helpers.py
from utils.helpers import remove_emojis

DATABASE_PATH = 'finance_bot.db'

#i use this router to manage simple user messages
user_private_router = Router()


@user_private_router.message(CommandStart())
async def command_start(message: Message):
    await message.answer("Welcome to finance bot. If you are not registered yet, please enter /register. Else you can view the list of commands with /commands")

@user_private_router.message(Command('commands'))
async def list_commands(message: Message):
    await message.answer("Here's the list: \n /commands - list of commands, \n /user_info - all info about you in db, \n /add_transaction - guess what it is, \n /report - view all incomes and expenses in custom period, \n /maxreport - like report but more detailed")


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
    await message.answer("📅 Please enter the **start date** for the report (format: DD-MM-YYYY):", reply_markup=cancel_keyboard)
    await state.set_state(ReportForm.start_date)

@user_private_router.message(ReportForm.start_date)
async def process_start_date(message: Message, state: FSMContext):
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return
    start_date_str = message.text.strip()
    try:
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        await state.update_data(start_date=start_date)
        await message.answer("📅 Please enter the **end date** for the report (format: DD-MM-YYYY):", reply_markup=cancel_keyboard)
        await state.set_state(ReportForm.end_date)
    except ValueError:
        await message.answer("❗ Invalid date format. Please enter the date in DD-MM-YYYY format.", reply_markup=cancel_keyboard)
    return

@user_private_router.message(ReportForm.end_date)
async def process_end_date(message: Message, state: FSMContext):
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return
    end_date_str = message.text.strip()
    data = await state.get_data()
    start_date = data.get('start_date')

    try:
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y")
        if end_date < start_date:
            await message.answer("❗ End date cannot be earlier than start date. Please enter a valid end date.", reply_markup=cancel_keyboard)
            return

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
            f"💰 Total Income: {total_income:.2f} $\n"
            f"💸 Total Expenses: {total_expense:.2f} $\n"
            f"📈 New Balance: {balance:.2f} $"
        )

        await message.answer(report_message, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        conn.close()
    except ValueError:
        await message.answer("❗ Invalid date format. Please enter the date in DD-MM-YYYY format.", reply_markup=cancel_keyboard)
        return

@user_private_router.message(F.text.casefold() == 'cancel', StateFilter('*'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Operation cancelled.", reply_markup=ReplyKeyboardRemove())
