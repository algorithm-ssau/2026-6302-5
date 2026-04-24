from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def mode_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧪 Training mode")],
            [KeyboardButton(text="🔥 Real interview mode")]
        ],
        resize_keyboard=True
    )