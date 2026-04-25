from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def commands_keyboard():
    """Клавиатура с основными командами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/help"), KeyboardButton(text="/stats")]
        ],
        resize_keyboard=True
    )