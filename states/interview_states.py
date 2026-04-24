from aiogram.fsm.state import StatesGroup, State

class InterviewState(StatesGroup):
    choosing_topic = State()
    choosing_level = State()
    choosing_mode = State()
    answering = State()
    real_mode = State()