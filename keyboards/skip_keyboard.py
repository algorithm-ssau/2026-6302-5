from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def skip_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить вопрос", callback_data="skip_question")]
        ]
    )