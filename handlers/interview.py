import uuid
import os
import re  

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.skip_keyboard import skip_button
from keyboards.level_keyboard import level_keyboard
from keyboards.end_keyboard import end_interview_keyboard

from states.interview_states import InterviewState
from services.interview_service import get_questions, get_next_question
from services.speech_service import transcribe_audio
from services.ai_service import evaluate_answer
from services.gigachat_auth import get_access_token
from config.settings import GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET
from services.stats_service import add_interview_result

router = Router()

@router.callback_query(F.data == "skip_question")
async def skip_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вопрос пропущен")
    
    data = await state.get_data()
    index = data["index"]
    questions = data["questions"]
    total_questions = len(questions)
    
    # Пропускаем вопрос (не оцениваем)
    index += 1
    next_q = get_next_question(questions, index)
    
    if next_q:
        await state.update_data(index=index)
        await callback.message.answer(
            f"⏭ Вопрос пропущен\n\n"
            f"Вопрос {index + 1} из {total_questions}:\n{next_q}",
            reply_markup=skip_button()
        )
    else:
        # Подсчет итоговых баллов при досрочном завершении
        total_score = data.get("total_score", 0)
        max_score = total_questions * 10
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        summary = f"""
🎉 Интервью завершено! 🎉

📊 Результаты:
━━━━━━━━━━━━━━━━━━━━
✅ Набрано баллов: {total_score} / {max_score}
📈 Процент: {percentage:.1f}%

💬 Оценка:
{"🌟 Отлично! Вы готовы к повышению!" if percentage >= 80 else 
"👍 Хорошо, но есть куда расти" if percentage >= 60 else
"📚 Рекомендуем подтянуть теорию"}
━━━━━━━━━━━━━━━━━━━━

Спасибо за участие! /start для новой попытки
"""
        await callback.message.answer(summary)
        await state.clear()
    
    await callback.message.delete()

@router.message(InterviewState.choosing_level)
async def choose_level(message: Message, state: FSMContext):
    level = message.text
    questions = get_questions(level)
    total_questions = len(questions)

    await state.update_data(
        level=level,
        questions=questions,
        index=0,
        total_score=0
    )

    await state.set_state(InterviewState.answering)

    # Меняем клавиатуру внизу (текст не пустой!)
    await message.answer(
        "✅ Интервью активно! Для ответа пришлите голосовое сообщение🎤",
        reply_markup=end_interview_keyboard()
    )

    await message.answer(
        f"📋 Всего вопросов: {total_questions}\n\n"
        f"Вопрос 1 из {total_questions}:\n{questions[0]}",
        reply_markup=skip_button()
    )

@router.message(InterviewState.answering, F.voice)
async def handle_voice(message: Message, state: FSMContext):
    data = await state.get_data()

    index = data["index"]
    questions = data["questions"]
    question = questions[index]
    total_questions = len(questions)

    await message.answer("🎙 Обрабатываю голос...")

    file = await message.bot.get_file(message.voice.file_id)
    file_path = file.file_path

    local_file = f"{uuid.uuid4()}.ogg"
    await message.bot.download_file(file_path, local_file)

    # Speech-to-text
    text = transcribe_audio(local_file)
    os.remove(local_file)

    await message.answer(f"📝 {text}")

    # GigaChat
    token = await get_access_token(
        GIGACHAT_CLIENT_ID,
        GIGACHAT_CLIENT_SECRET
    )

    result = await evaluate_answer(token, question, text)

    await message.answer(f"📊 {result}")

    # Парсим оценку из ответа GigaChat
    score_match = re.search(r'(\d+)/10', result)
    current_score = 0
    if score_match:
        current_score = int(score_match.group(1))
        total_score = data.get("total_score", 0) + current_score
        await state.update_data(total_score=total_score)
        await message.answer(f"✅ +{current_score} баллов")
    else:
        await message.answer("⚠️ Не удалось распознать оценку")

    # следующий вопрос
    index += 1
    next_q = get_next_question(questions, index)

    if next_q:
        await state.update_data(index=index)
        await message.answer(
            f"📊 Текущий счет: {total_score if score_match else data.get('total_score', 0)}/{total_questions * 10}\n\n"
            f"Вопрос {index + 1} из {total_questions}:\n{next_q}",
            reply_markup=skip_button()
        )
    else:
        # Интервью завершено - показываем итоговый результат
        final_score = data.get("total_score", 0)
        if score_match:
            final_score = total_score
        max_score = total_questions * 10
        percentage = (final_score / max_score) * 100

        answers_list = []  
        add_interview_result(
            user_id=message.from_user.id,
            level=data.get("level", "Unknown"),
            total_questions=total_questions,
            total_score=final_score,
            max_score=max_score,
            answers=answers_list
        )
        
        summary = f"""
🎉 Интервью завершено! 🎉

📊 Результаты:
━━━━━━━━━━━━━━━━━━━━
✅ Набрано баллов: {final_score} / {max_score}
📈 Процент: {percentage:.1f}%

💬 Оценка:
{"🌟 Отлично! Вы готовы к повышению!" if percentage >= 80 else 
"👍 Хорошо, но есть куда расти" if percentage >= 60 else
"📚 Рекомендуем подтянуть теорию"}
━━━━━━━━━━━━━━━━━━━━

Спасибо за участие! /start для новой попытки
"""
        await message.answer(summary)
        await state.clear()

@router.message(F.text == "❌ Завершить интервью")
async def finish_interview_early(message: Message, state: FSMContext):
    """Досрочное завершение интервью"""
    
    data = await state.get_data()
    
    # Если интервью не активно
    if not data:
        await message.answer(
            "👋 Нет активного интервью.\n/start чтобы начать",
            reply_markup=level_keyboard()
        )
        return
    
    # Достаем данные
    total_questions = len(data.get("questions", []))
    total_score = data.get("total_score", 0)
    max_score = total_questions * 10
    
    # Считаем процент
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Сохраняем в статистику
    add_interview_result(
        user_id=message.from_user.id,
        level=data.get("level", "Unknown"),
        total_questions=total_questions,
        total_score=total_score,
        max_score=max_score,
        answers=[]
    )
    
    # Показываем результат
    summary = f"""
🎉 Интервью завершено досрочно!

📊 Результаты:
━━━━━━━━━━━━━━━━━━━━
✅ Вопросов пройдено: {data.get('index', 0)} из {total_questions}
✅ Набрано баллов: {total_score} / {max_score}
📈 Процент: {percentage:.1f}%

💬 Оценка:
{"🌟 Отлично!" if percentage >= 80 else 
"👍 Хорошо" if percentage >= 60 else
"📚 Надо подтянуть"}
━━━━━━━━━━━━━━━━━━━━

/start для новой попытки
"""
    
    await message.answer(summary, reply_markup=level_keyboard())
    await state.clear()