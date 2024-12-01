from aiogram import types, Router, F, html
from aiogram.filters import Command, CommandStart, StateFilter
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import sqlite3

from database.db import add_user

DATABASE_PATH = 'finance_bot.db'

user_register_router = Router()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class UserRegister(StatesGroup):
    user_id = State()
    first_name = State()
    budget = State()
    balance = State()

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Cancel')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@user_register_router.message(Command('register'))
async def register_command(message: Message, state: FSMContext) -> None:
    await state.set_state(UserRegister.first_name)
    await message.reply(
        "Welcome to the Finance Bot! Let's register you. Please enter your name:",
        reply_markup=cancel_keyboard
    )

@user_register_router.message(UserRegister.first_name)
async def registration_1(message: Message, state: FSMContext) -> None:
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return
    await state.update_data(first_name=message.text, user_id=message.from_user.id)
    await state.set_state(UserRegister.budget)
    await message.answer(
        f"Nice to meet you, {html.quote(message.text)}!\nHow much money would you like to spend monthly $$?",
        reply_markup=cancel_keyboard
    )

@user_register_router.message(UserRegister.budget)
async def registration_2(message: Message, state: FSMContext) -> None:
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return
    try:
        budget = float(message.text)
        await state.update_data(budget=budget)
    except ValueError:
        await message.reply("Please enter a valid number for the budget.", reply_markup=cancel_keyboard)
        return

    await state.set_state(UserRegister.balance)
    await message.answer(
        "Then, how much money do you have now $$?",
        reply_markup=cancel_keyboard
    )

@user_register_router.message(UserRegister.balance)
async def registration_3(message: Message, state: FSMContext) -> None:
    if message.text.strip().lower() == 'cancel':
        await cancel_handler(message, state)
        return
    try:
        balance = float(message.text)
        await state.update_data(balance=balance)
    except ValueError:
        await message.reply("Please enter a valid number for the balance.", reply_markup=cancel_keyboard)
        return

    current_state = await state.get_data()
    user_id = current_state.get('user_id')
    first_name = current_state.get('first_name')
    budget = current_state.get('budget')
    balance = current_state.get('balance')

    try:
        await add_user(user_id, first_name, budget, balance)
    except Exception as e:
        await message.reply("An error occurred while saving your data. Please try again later.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    await state.clear()
<<<<<<< HEAD
    await message.reply("Registration complete! Your information has been saved. Here's some commands /commands")
    await message.answer(f"{current_state}")
=======
    await message.reply("Registration complete! Your information has been saved. Here's some commands: /commands", reply_markup=ReplyKeyboardRemove())
    await message.answer(f"{current_state}")

@user_register_router.message(F.text.casefold() == 'cancel', StateFilter('*'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Operation cancelled.", reply_markup=ReplyKeyboardRemove())
>>>>>>> 28ca59c (main part is done)
