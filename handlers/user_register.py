from aiogram import types, Router, F, html
from aiogram.filters import Command, CommandStart
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User, Message
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

@user_register_router.message(Command('register'))
async def register_command(message: Message, state: FSMContext) -> None:
    await state.set_state(UserRegister.first_name)
    await message.reply("Welcome to the Finance Bot! Let's register you. Please enter your name:")


@user_register_router.message(UserRegister.first_name)
async def registration_1(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text, user_id=message.from_user.id)
    await state.set_state(UserRegister.budget)
    await message.answer(f"Nice to meet you, {html.quote(message.text)}!\nHow much money would you like to spend monthly $$$?")


@user_register_router.message(UserRegister.budget)
async def registration_2(message: Message, state: FSMContext) -> None:
    try:
        budget = int(message.text)
        await state.update_data(budget=budget)
    except ValueError:
        await message.reply("Please enter a valid number for the budget.")
        return

    await state.set_state(UserRegister.balance)
    await message.answer("Then, how much money do you have now $$$?")


@user_register_router.message(UserRegister.balance)
async def registration_3(message: Message, state: FSMContext) -> None:
    try:
        balance = int(message.text)
        await state.update_data(balance=balance)
    except ValueError:
        await message.reply("Please enter a valid number for the balance.")
        return
    
    current_state = await state.get_data()

    print(current_state)

    user_id = current_state.get('user_id')
    first_name = current_state.get('first_name')
    budget = current_state.get('budget')
    balance = current_state.get('balance')

    await add_user(user_id, first_name, budget, balance)
    await state.clear()
    await message.reply("Registration complete! Your information has been saved. Here's some commands /commands")
    await message.answer(f"{current_state}")