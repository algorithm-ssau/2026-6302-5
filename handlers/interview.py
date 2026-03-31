import uuid
import os

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.skip_keyboard import skip_button

from states.interview_states import InterviewState
from services.interview_service import get_questions, get_next_question
from services.speech_service import transcribe_audio
from services.ai_service import evaluate_answer
from services.gigachat_auth import get_access_token
from config.settings import GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET

router = Router()

@router.callback_query(F.data == "skip_question")
async def skip_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вопрос пропущен")
    
    data = await state.get_data()
    index = data["index"]
    questions = data["questions"]
    
    # Пропускаем вопрос (не оцениваем)
    index += 1
    next_q = get_next_question(questions, index)
    
    if next_q:
        await state.update_data(index=index)
        await callback.message.answer(f"Следующий вопрос:\n{next_q}")
    else:
        await callback.message.answer("🎉 Интервью завершено!")
        await state.clear()
    
    await callback.message.delete()

@router.message(InterviewState.choosing_level)
async def choose_level(message: Message, state: FSMContext):
    level = message.text
    questions = get_questions(level)

    await state.update_data(
        level=level,
        questions=questions,
        index=0,
        total_score=0
    )

    await state.set_state(InterviewState.answering)

    await message.answer(
    f"Вопрос 1:\n{questions[0]}",
    reply_markup=skip_button()
)


@router.message(InterviewState.answering, F.voice)
async def handle_voice(message: Message, state: FSMContext):
    data = await state.get_data()

    index = data["index"]
    questions = data["questions"]
    question = questions[index]

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

    # следующий вопрос
    index += 1
    next_q = get_next_question(questions, index)

    if next_q:
        await state.update_data(index=index)
        await message.answer(
            f"Следующий вопрос:\n{next_q}",
            reply_markup=skip_button()  # ✅ Добавлена кнопка
        )
    else:
        await message.answer("🎉 Интервью завершено!")
        await state.clear()