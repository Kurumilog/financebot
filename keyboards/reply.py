from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Text

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Cancel')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

