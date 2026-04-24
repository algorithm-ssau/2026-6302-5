from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.topic_keyboard import topic_keyboard
from states.interview_states import InterviewState

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(InterviewState.choosing_topic)
    await message.answer(
        "🚀 Привет! Я AI-интервьюер\n\n"
        "Выберите тему для интервью:",
        reply_markup=topic_keyboard()
    )


@router.message(Command("help"))
async def help_command(message: Message):
    """Отправляет инструкцию по использованию бота"""

    help_text = """
🤖 *AI-Интервьюер — инструкция*

*Как пользоваться:*
1️⃣ Выберите уровень сложности: Junior / Middle / Senior
2️⃣ Отвечайте на вопросы голосом
3️⃣ После ответа получите оценку от 0 до 10 и обратную связь
4️⃣ Используйте кнопки управления:
   • ⏭ *Пропустить* — перейти к следующему вопросу
   • ❌ *Завершить* — завершить интервью досрочно

*Доступные команды:*
/start — начать новое интервью
/help — показать эту инструкцию
/stats — посмотреть статистику прошлых интервью

*Советы:*
• Отвечайте развернуто, это повышает оценку
• Голосовые сообщения автоматически расшифровываются
• Результаты сохраняются в вашу статистику

Удачи! 🚀
"""

    await message.answer(
        help_text,
        parse_mode="Markdown"
    )


@router.message(Command("stats"))
async def stats_command(message: Message):
    """Показывает статистику интервью"""
    from services.stats_service import load_stats

    stats = load_stats(message.from_user.id)

    if not stats or "interviews" not in stats or not stats["interviews"]:
        await message.answer(
            "📊 *Статистика*\n\n"
            "У вас пока нет завершенных интервью.\n"
            "Пройдите интервью с помощью /start!",
            parse_mode="Markdown"
        )
        return

    interviews = stats["interviews"]
    total = len(interviews)
    avg_percentage = sum(i["percentage"] for i in interviews) / total

    result = f"📊 *Ваша статистика*\n\n"
    result += f"*Всего интервью:* {total}\n"
    result += f"*Средний результат:* {avg_percentage:.1f}%\n\n"
    result += f"*Последние интервью:*\n"

    for i in interviews[-3:]:
        emoji = "🟢" if i["percentage"] >= 80 else "🟡" if i["percentage"] >= 60 else "🔴"
        result += f"{emoji} {i['date'][:10]} | {i['level']} | {i['total_score']}/{i['max_score']} ({i['percentage']}%)\n"

    await message.answer(result, parse_mode="Markdown")
