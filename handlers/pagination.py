from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

from database.db import get_db_connection


DATABASE_PATH = 'finance_bot.db'

pagination_router = Router()


def get_transactions_page(user_id: int, page: int, per_page: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM UserTransaction WHERE user_id = ?', (user_id,))
    total_records = cursor.fetchone()[0]

    total_pages = (total_records + per_page - 1) // per_page

    offset = (page - 1) * per_page
    cursor.execute('''
        SELECT * FROM UserTransaction 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    ''', (user_id, per_page, offset))

    transactions = cursor.fetchall()
    conn.close()

    return transactions, total_pages

def create_transactions_keyboard(current_page: int, total_pages: int):
    keyboard = []

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️", 
            callback_data=f"page_{current_page-1}"
        ))

    nav_buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="current_page"
    ))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data=f"page_{current_page+1}"
        ))

    keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def format_transaction(transaction):
    emoji = "💰" if transaction['transaction_type'] == 'income' else "💸"

    amount = f"{transaction['amount']:.2f}"

    return (f"{emoji} {transaction['category']} | {amount} $ | "
            f"{transaction['created_at']}")

@pagination_router.message(Command("transactions"))
async def show_transactions(message: types.Message):
    user_id = message.from_user.id
    page = 1
    transactions, total_pages = get_transactions_page(user_id, page)

    if not transactions:
        await message.answer("У вас пока нет транзакций.")
        return

    text = "📊 Ваши транзакции:\n\n"
    for trans in transactions:
        text += format_transaction(trans) + "\n"

    keyboard = create_transactions_keyboard(page, total_pages)

    await message.answer(text, reply_markup=keyboard)

@pagination_router.callback_query(lambda c: c.data.startswith('page_'))
async def process_page_callback(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id

    transactions, total_pages = get_transactions_page(user_id, page)

    text = "📊 Ваши транзакции:\n\n"
    for trans in transactions:
        text += format_transaction(trans) + "\n"

    keyboard = create_transactions_keyboard(page, total_pages)

    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()