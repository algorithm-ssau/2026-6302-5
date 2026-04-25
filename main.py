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

#команда /status
@dp.message(Command("status"))
async def check_status(message: Message, state: FSMContext):
    """Проверка текущего состояния интервью"""
    current_state = await state.get_state()
    data = await state.get_data()

    if not current_state or "questions" not in data:
        await message.answer("📊 Нет активного интервью\nИспользуй /start")
        return

    index = data.get("index", 0)
    questions = data["questions"]
    total = len(questions)
    answered = data.get("answered_current", False)
    is_real = data.get("is_real", False)

    status_text = f"🎯 Текущий вопрос: {index + 1}/{total}\n"
    status_text += f"✅ Ответ дан: {'Да' if answered else 'Нет'}\n"
    status_text += f"🔥 Режим: {'Real' if is_real else 'Training'}\n"
    status_text += f"📊 Набрано баллов: {data.get('total_score', 0)}"

    await message.answer(status_text)

if __name__ == "__main__":
    asyncio.run(main())