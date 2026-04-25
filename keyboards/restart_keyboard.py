from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def restart_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой для повторного прохождения"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Пройти еще раз")],
            [KeyboardButton(text="❌ Закрыть")]
        ],
        resize_keyboard=True
    )