#i use this class with FSMcontext(redis db from aiogram) to track user steps
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.methods.delete_messages import DeleteMessages
from datetime import datetime
import sqlite3

#importing keyboards from keyboards/reply_keyboards.py
from keyboards.reply_keyboards import categories_keyboard, transaction_type_keyboard
from keyboards.reply_keyboards import cancel_keyboard

#importing func from database/db.py 
from database.db import get_db_connection

#you can read the descriptin of this func in utils/helpers.py
from utils.helpers import remove_emojis

DATABASE_PATH = 'finance_bot.db'

transaction_router = Router()


class TransactionForm(StatesGroup):
    transaction_type = State()
    category = State()
    custom_category = State()
    amount = State()


@transaction_router.message(Command('add_transaction'))
async def add_transaction_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Please select the type of transaction:",
        reply_markup=transaction_type_keyboard()
    )
    await state.set_state(TransactionForm.transaction_type)
    


@transaction_router.message(TransactionForm.transaction_type)
async def process_transaction_type(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return

    transaction_input = message.text.strip()
    if transaction_input in ['💰 Income', 'Income', '💸 Expense', 'Expense']:
        if 'Income' in transaction_input:
            transaction_type = 'income'
        else:
            transaction_type = 'expense'
        await state.update_data(transaction_type=transaction_type)
        await message.answer(
            "Please select the category of the transaction:",
            reply_markup=categories_keyboard()
        )
        await state.set_state(TransactionForm.category)
    else:
        await message.answer(
            "❗ Please select a valid transaction type from the keyboard.",
            reply_markup=cancel_keyboard
        )


@transaction_router.message(TransactionForm.category)
async def process_category(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return

    category = message.text.strip()
    allowed_categories = [
        '🍔 Food', '🚌 Transport', '🛍️ Shopping', '💡 Utilities',
        '💼 Salary', '📈 Investment', 'Other'
    ]

    if category not in allowed_categories:
        await message.answer(
            "❗ Please select a category from the keyboard.",
            reply_markup=cancel_keyboard
        )
        return

    if category == 'Other':
        await message.answer(
            "Please enter the category:",
            reply_markup=cancel_keyboard
        )
        await state.set_state(TransactionForm.custom_category)
    else:
        plain_category = remove_emojis(category)
        await state.update_data(category=plain_category)
        await message.answer(
            "Please enter the amount of the transaction:",
            reply_markup=cancel_keyboard
        )
        await state.set_state(TransactionForm.amount)


@transaction_router.message(TransactionForm.custom_category)
async def process_custom_category(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return

    category = message.text.strip()
    await state.update_data(category=category)
    await message.answer(
        "Please enter the amount of the transaction:",
        reply_markup=cancel_keyboard
    )
    await state.set_state(TransactionForm.amount)


@transaction_router.message(TransactionForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return

    text_input = message.text.strip()
    try:
        amount = int(text_input)
    except ValueError:
        try:
            amount = float(text_input)
        except ValueError:
            await message.answer(
                "❗ Please enter a valid amount using numbers only (e.g., 100 or 100.50).",
                reply_markup=cancel_keyboard
            )
            return

    await state.update_data(amount=amount)
    data = await state.get_data()
    user_id = message.from_user.id
    amount = data['amount']
    category = data['category']
    transaction_type = data['transaction_type']
    created_at = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO UserTransaction (user_id, amount, category, transaction_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, category, transaction_type, created_at))
    conn.commit()
    conn.close()

    await message.answer(
        "✅ Transaction successfully added!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@transaction_router.message(F.text.casefold() == 'cancel', StateFilter('*'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Operation cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )