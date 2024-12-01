from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def transaction_type_keyboard():
  builder = ReplyKeyboardBuilder()
  builder.button(text='💰 Income')
  builder.button(text='💸 Expense')
  builder.adjust(2)
  return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def categories_keyboard():
  builder = ReplyKeyboardBuilder()
  categories = ['🍔 Food', '🚌 Transport', '🛍️ Shopping', '💡 Utilities', '💼 Salary', '📈 Investment', 'Other']
  for category in categories:
      builder.button(text=category)
  builder.adjust(2)
  return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)