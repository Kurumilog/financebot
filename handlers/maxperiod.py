from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InputFile
import asyncio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
from functools import partial
from datetime import datetime
import sqlite3
import logging


logging.basicConfig(level=logging.DEBUG)

DATABASE_PATH = 'finance_bot.db'

maxperiod_router = Router()


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class MaxPeriodForm(StatesGroup):
    start_date = State()
    end_date = State()

def normalize_date_input(date_str):
    date_str = date_str.strip()
    date_str = date_str.replace('–', '-').replace('—', '-').replace('−', '-').replace('/', '-')
    parts = date_str.split('-')
    if len(parts) != 3:
        return None
    day, month, year = parts
    day = day.zfill(2)
    month = month.zfill(2)
    normalized_date_str = f"{day}-{month}-{year}"
    return normalized_date_str
    print(normalized_date_str)

def generate_plots(df):
    images = []

    income_data = df[df['transaction_type'] == 'income']
    expense_data = df[df['transaction_type'] == 'expense']

    if not income_data.empty:
        fig_income, ax_income = plt.subplots(figsize=(6, 6))
        ax_income.pie(
            income_data['total_amount'],
            labels=income_data['category'],
            autopct='%1.1f%%',
            startangle=140
        )
        ax_income.set_title('Income by Category')

        image_io_income = io.BytesIO()
        fig_income.savefig(image_io_income, format='png')
        image_io_income.seek(0)
        plt.close(fig_income)
        images.append(('Income by Category', image_io_income))

    if not expense_data.empty:
        fig_expense, ax_expense = plt.subplots(figsize=(6, 6))
        ax_expense.pie(
            expense_data['total_amount'],
            labels=expense_data['category'],
            autopct='%1.1f%%',
            startangle=140
        )
        ax_expense.set_title('Expenses by Category')

        image_io_expense = io.BytesIO()
        fig_expense.savefig(image_io_expense, format='png')
        image_io_expense.seek(0)
        plt.close(fig_expense)
        images.append(('Expenses by Category', image_io_expense))

    return images

@maxperiod_router.message(Command('maxperiod'))
async def maxperiod_start(message: Message, state: FSMContext):
    await message.answer("📅 Please enter the **start date** for the analytics (format: DD-MM-YYYY):")
    await state.set_state(MaxPeriodForm.start_date)

@maxperiod_router.message(MaxPeriodForm.start_date)
async def process_maxperiod_start_date(message: Message, state: FSMContext):
    start_date_str = message.text.strip()
    logging.debug(f"Original start date input: {start_date_str}")
    normalized_date_str = normalize_date_input(start_date_str)
    logging.debug(f"Normalized start date input: {normalized_date_str}")
    if not normalized_date_str:
        await message.answer("❗ Invalid date format. Please enter the date in DD-MM-YYYY format (e.g., 01-12-2024).")
        return

    try:
        start_date = datetime.strptime(normalized_date_str, "%d-%m-%Y")
    except ValueError:
        await message.answer("❗ Invalid date. Please ensure the date exists and is in DD-MM-YYYY format (e.g., 01-12-2024).")
        return

    await state.update_data(start_date=start_date)
    await message.answer("📅 Please enter the **end date** for the analytics (format: DD-MM-YYYY):")
    await state.set_state(MaxPeriodForm.end_date)


@maxperiod_router.message(MaxPeriodForm.end_date)
async def process_maxperiod_end_date(message: Message, state: FSMContext):
    end_date_str = message.text.strip()
    logging.debug(f"Original end date input: {end_date_str}")
    normalized_date_str = normalize_date_input(end_date_str)
    logging.debug(f"Normalized end date input: {normalized_date_str}")
    if not normalized_date_str:
        await message.answer("❗ Invalid date format. Please enter the date in DD-MM-YYYY format (e.g., 01-12-2024).")
        return

    data = await state.get_data()
    start_date = data.get('start_date')

    try:
        end_date = datetime.strptime(normalized_date_str, "%d-%m-%Y")
    except ValueError:
        await message.answer("❗ Invalid date. Please ensure the date exists and is in DD-MM-YYYY format (e.g., 01-12-2024).")
        return

    if end_date < start_date:
        await message.answer("❗ End date cannot be earlier than the start date. Please enter a valid end date.")
        return

    await generate_and_send_plots(message, state, start_date, end_date)


async def generate_and_send_plots(message: Message, state: FSMContext, start_date: datetime, end_date: datetime):
    try:
        start_date_db = start_date.strftime('%Y-%m-%d')
        end_date_db = end_date.strftime('%Y-%m-%d')

        user_id = message.from_user.id
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT category, transaction_type, SUM(amount) as total_amount
            FROM UserTransaction
            WHERE user_id = ? AND
                  DATE(created_at) BETWEEN DATE(?) AND DATE(?)
            GROUP BY category, transaction_type
        ''', (user_id, start_date_db, end_date_db))
        results = cursor.fetchall()
        conn.close()

        if not results:
            await message.answer("No transactions found for the specified period.")
            await state.clear()
            return

        df = pd.DataFrame(results)
        df.columns = ['category', 'transaction_type', 'total_amount']

        loop = asyncio.get_running_loop()
        images = await loop.run_in_executor(None, partial(generate_plots, df))
        logging.debug(f"Generated images: {images}")

        for title, image_io in images:
            logging.debug(f"Sending image: {title}")
            image_io.seek(0)
            photo = InputFile(image_io, filename='plot.png')
            await message.answer_photo(photo=photo, caption=title)

    except Exception as e:
        logging.exception("An error occurred during plot generation or sending.")
        await message.answer("An error occurred while generating the report. Please try again later.")
    finally:
        await state.clear()