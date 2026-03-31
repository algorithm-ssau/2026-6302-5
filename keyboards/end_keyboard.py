from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def end_interview_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Завершить интервью")]
        ],
        resize_keyboard=True
    )