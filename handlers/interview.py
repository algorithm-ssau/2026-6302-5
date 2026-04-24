import os
import re
import uuid
import asyncio
import time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from config.settings import GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET
from keyboards.end_keyboard import end_interview_keyboard
from keyboards.level_keyboard import level_keyboard
from keyboards.mode_keyboard import mode_keyboard
from keyboards.skip_keyboard import skip_button
from keyboards.topic_keyboard import topic_keyboard
from services.ai_service import evaluate_answer
from services.gigachat_auth import get_access_token
from services.interview_service import finish_interview
from services.interview_service import get_questions, get_next_question, get_topics
from services.speech_service import transcribe_audio
from states.interview_states import InterviewState

router = Router()
TIME_FOR_QUESTION = 60


@router.message(InterviewState.choosing_topic)
async def choose_topic(message: Message, state: FSMContext):
    topic = message.text.replace("🐍 ", "").replace("☕ ", "").replace("🗄 ", "").replace("📦 ", "")

    if topic not in get_topics():
        await message.answer("Выберите тему:", reply_markup=topic_keyboard())
        return

    await state.update_data(topic=topic)
    await state.set_state(InterviewState.choosing_level)

    await message.answer(
        f"📚 Тема: {topic}\n\nВыберите уровень:",
        reply_markup=level_keyboard()
    )

@router.message(InterviewState.choosing_level)
async def choose_level(message: Message, state: FSMContext):
    level = message.text

    await state.update_data(level=level)
    await state.set_state(InterviewState.choosing_mode)

    await message.answer(
        f"🎚 Уровень: {level}\n\nВыберите режим:",
        reply_markup=mode_keyboard()
    )

@router.message(InterviewState.choosing_mode)
async def choose_mode(message: Message, state: FSMContext):
    mode = message.text

    if mode not in ["🧪 Training mode", "🔥 Real interview mode"]:
        await message.answer("Выберите режим кнопкой")
        return

    is_real = mode.startswith("🔥")

    data = await state.get_data()
    topic = data["topic"]
    level = data["level"]

    questions = get_questions(topic, level)

    await state.update_data(
        mode=mode,
        is_real=is_real,
        index=0,
        total_score=0,
        answers=[],
        questions=questions,
        timer_task=None,
        answered_current=False,
        current_question_id=0
    )

    await state.set_state(InterviewState.answering)

    await message.answer(
        f"✅ Интервью начато!\nРежим: {mode}\nОтвечай голосом 🎤",
        reply_markup=end_interview_keyboard()
    )

    await message.answer(
        f"📋 Вопрос 1:\n{questions[0]}",
        reply_markup=skip_button()
    )

    # старт таймера если real mode
    if is_real:
        timer_msg = await message.answer(f"⏱ Осталось времени: {TIME_FOR_QUESTION} сек")
        await state.update_data(timer_message_id=timer_msg.message_id)
        task = asyncio.create_task(real_mode_timer(message, state, 0))
        await state.update_data(timer_task=task)


@router.callback_query(F.data == "skip_question")
async def skip_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get("is_real"):
        await callback.answer("❌ Нельзя пропускать в real mode", show_alert=True)
        return

    await callback.answer("Пропущено")

    index = data["index"] + 1
    questions = data["questions"]

    if index < len(questions):
        await state.update_data(
            index=index,
            answered_current=False,
            current_question_id=index
        )

        await callback.message.answer(
            f"⏭ Вопрос {index + 1}:\n{questions[index]}",
            reply_markup=skip_button()
        )

    else:
        await finish_interview(
            state=state,
            user_id=callback.from_user.id,
            total_questions=len(questions),
            message=callback.message
        )

    await callback.message.delete()


@router.message(InterviewState.answering, F.voice)
async def handle_voice(message: Message, state: FSMContext):
    data = await state.get_data()

    # cancel timer
    task = data.get("timer_task")
    if task:
        task.cancel()

    index = data["index"]
    questions = data["questions"]
    question = questions[index]

    is_real = data.get("is_real", False)

    await state.update_data(answered_current=True)

    await message.answer("🎙 Обрабатываю...")

    file = await message.bot.get_file(message.voice.file_id)
    file_path = file.file_path

    local_file = f"{uuid.uuid4()}.ogg"
    await message.bot.download_file(file_path, local_file)

    text = transcribe_audio(local_file)
    os.remove(local_file)

    await message.answer(f"📝 {text}")

    token = await get_access_token(
        GIGACHAT_CLIENT_ID,
        GIGACHAT_CLIENT_SECRET
    )

    evaluation = await evaluate_answer(token, question, text)

    score = evaluation.get("score", 0)
    pros = evaluation.get("pros", [])
    cons = evaluation.get("cons", [])
    feedback = evaluation.get("feedback", "")
    recommendations = evaluation.get("recommendations", [])

    if is_real:
        score = max(0, score - 1)

    answers = data.get("answers", [])
    answers.append({
        "question": question,
        "answer": text,
        "score": score,
        "feedback": feedback
    })

    await state.update_data(
        answers=answers,
        total_score=data.get("total_score", 0) + score
    )

    await message.answer(
        f"""📊 Оценка: {score}/10

💪 Плюсы:
{chr(10).join('• ' + p for p in pros) if pros else '—'}

⚠️ Минусы:
{chr(10).join('• ' + c for c in cons) if cons else '—'}

🧠 Фидбек:
{feedback}

🚀 Рекомендации:
{chr(10).join('• ' + r for r in recommendations) if recommendations else '—'}
"""
    )

    await go_next_question(
        message=message,
        state=state,
        question_id=index,
        is_real=is_real
    )


async def real_mode_timer(message: Message, state: FSMContext, question_id: int, delay: int = TIME_FOR_QUESTION):
    try:
        chat_id = message.chat.id

        for remaining in range(delay, 0, -1):
            await asyncio.sleep(1)

            data = await state.get_data()

            # если вопрос сменился — стоп
            if data.get("current_question_id") != question_id:
                return

            if data.get("answered_current"):
                return

            # if remaining % 5 == 0 or remaining <= 10:
            try:
                await message.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=data.get("timer_message_id"),
                    text=f"⏱ Осталось времени: {remaining} сек"
                )
            except:
                pass

        # время вышло
        data = await state.get_data()

        if data.get("answered_current"):
            return

        await message.answer("⏱ Время вышло!")

        await go_next_question(
            message,
            state,
            question_id,
            data.get("is_real", False)
        )

    except asyncio.CancelledError:
        return


async def go_next_question(message: Message, state: FSMContext, question_id: int, is_real: bool):
    data = await state.get_data()

    questions = data["questions"]
    total_questions = len(questions)

    new_index = question_id + 1

    if new_index >= total_questions:
        await finish_interview(
            state=state,
            user_id=message.from_user.id,
            total_questions=total_questions,
            message=message
        )
        return

    next_q = questions[new_index]

    await state.update_data(
        index=new_index,
        current_question_id=new_index,
        answered_current=False
    )

    await message.answer(
        f"📊 Переход к следующему вопросу\n\n"
        f"Вопрос {new_index + 1}:\n{next_q}",
        reply_markup=skip_button()
    )

    if is_real:
        timer_msg = await message.answer(f"⏱ Осталось времени: {TIME_FOR_QUESTION} сек")

        await state.update_data(timer_message_id=timer_msg.message_id)

        task = asyncio.create_task(
            real_mode_timer(message, state, new_index)
        )

        await state.update_data(timer_task=task)


@router.message(F.text == "❌ Завершить интервью")
async def finish_interview_early(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data or "questions" not in data:
        await message.answer("❌ Нет активного интервью")
        return

    task = data.get("timer_task")
    if task:
        task.cancel()

    await finish_interview(
        state=state,
        user_id=message.from_user.id,
        total_questions=len(data["questions"]),
        message=message
    )
