import os
import re
import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from config.settings import GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET
from keyboards.end_keyboard import end_interview_keyboard
from keyboards.level_keyboard import level_keyboard
from keyboards.skip_keyboard import skip_button
from keyboards.topic_keyboard import topic_keyboard
from services.ai_service import evaluate_answer
from services.gigachat_auth import get_access_token
from services.interview_service import finish_interview
from services.interview_service import get_questions, get_next_question, get_topics
from services.speech_service import transcribe_audio
from states.interview_states import InterviewState

router = Router()


@router.message(InterviewState.choosing_topic)
async def choose_topic(message: Message, state: FSMContext):
    topic = message.text.replace("🐍 ", "").replace("☕ ", "").replace("🗄 ", "").replace("📦 ", "")

    if topic not in get_topics():
        await message.answer("Выберите тему, нажав одну из кнопок ниже:", reply_markup=topic_keyboard())
        return

    await state.update_data(topic=topic)
    await state.set_state(InterviewState.choosing_level)

    await message.answer(
        f"Вы выбрали тему: {topic}\n\nВыберите уровень сложности:",
        reply_markup=level_keyboard()
    )


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
        await finish_interview(
            state=state,
            user_id=callback.from_user.id,
            total_questions=total_questions,
            message=callback.message
        )

    await callback.message.delete()


@router.message(InterviewState.choosing_level)
async def choose_level(message: Message, state: FSMContext):
    level = message.text
    data = await state.get_data()
    topic = data.get("topic")

    if not topic:
        await state.set_state(InterviewState.choosing_topic)
        await message.answer("Сначала выберите тему:", reply_markup=topic_keyboard())
        return

    questions = get_questions(topic, level)

    if not questions:
        await message.answer(f"Нет вопросов для {topic} - {level}. Попробуйте другой уровень.")
        return

    total_questions = len(questions)

    await state.update_data(
        level=level,
        questions=questions,
        index=0,
        total_score=0
    )

    await state.set_state(InterviewState.answering)

    await message.answer(
        "✅ Интервью активно! Для ответа пришлите голосовое сообщение🎤",
        reply_markup=end_interview_keyboard()
    )

    await message.answer(
        f"📋 Тема: {topic} | Уровень: {level}\n"
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
    else:
        await message.answer("⚠️ Не удалось распознать оценку")

    total_score = data.get("total_score", 0) + current_score
    await state.update_data(total_score=total_score)

    # следующий вопрос
    index += 1

    if index < len(questions):
        print("INDEX:", index, "LEN:", len(questions))
        next_q = questions[index]
        await state.update_data(index=index)

        await message.answer(
            f"📊 Текущий счет: {data.get('total_score', 0)}/{total_questions * 10}\n\n"
            f"Вопрос {index + 1} из {total_questions}:\n{next_q}",
            reply_markup=skip_button()
        )
    else:
        await finish_interview(
            state=state,
            user_id=message.from_user.id,
            total_questions=total_questions,
            message=message
        )


@router.message(F.text == "❌ Завершить интервью")
async def finish_interview_early(message: Message, state: FSMContext):
    print("🔥 FINISH BUTTON WORKED")
    """Досрочное завершение интервью"""

    # Если интервью не активно
    data = await state.get_data()

    if not data or "questions" not in data:
        await message.answer("Нет активного интервью")
        return

    # Достаем данные
    total_questions = len(data.get("questions", []))

    await finish_interview(
        state=state,
        user_id=message.from_user.id,
        total_questions=total_questions,
        message=message
    )
