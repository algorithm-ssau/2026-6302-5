import asyncio
from aiogram import Bot, Dispatcher

from config.settings import BOT_TOKEN
from handlers import start, interview
from bot_commands import set_bot_commands

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(interview.router)

async def main():

    await set_bot_commands(bot)
    await dp.start_polling(bot)

#команда /cancel
@dp.message(Command("cancel"))
async def cancel_interview(message: Message, state: FSMContext):
    """Отмена текущего интервью"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного интервью")
        return

    await state.clear()
    await message.answer(
        "❌ Интервью отменено\n\n"
        "Чтобы начать заново, используй /start",
        reply_markup=ReplyKeyboardRemove()
    )

if __name__ == "__main__":
    asyncio.run(main())