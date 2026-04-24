from aiogram.types import ReplyKeyboardRemove

from keyboards.topic_keyboard import topic_keyboard

# Новая структура: тема → уровень → список вопросов (по 2 вопроса для теста)
QUESTIONS = {
    "Python": {
        "Junior": [
            "Что такое PEP8?",
            "Чем отличается list от tuple?",
            "Что такое GIL?",
            "Какие типы данных в Python являются неизменяемыми?",
            "Что такое декоратор?",
            "Чем отличается `==` от `is`?",
            "Что такое list comprehension?",
            "Как работает `with` (контекстный менеджер)?",
            "Что такое `__init__`?",
            "Чем отличается `append` от `extend`?"
        ],
        "Middle": [
            "Как работает сборщик мусора в Python?",
            "Что такое asyncio?",
            "Чем отличается процесс от потока?",
            "Как работает GIL и как его обойти?",
            "Что такое дескрипторы?",
            "Какие паттерны проектирования используются в Python?",
            "Что такое `__slots__`?",
            "Как работает управление памятью в Python?",
            "Что такое декораторы классов?"
        ],
        "Senior": [
            "Как устроен интерпретатор CPython?",
            "Что такое GIL-free Python?",
            "Как оптимизировать производительность Python-кода?",
            "Что такое профилирование и какие инструменты используете?",
            "Как отлаживать утечки памяти в Python?",
            "Что такое GIL-free Python (subinterpreters)?",
            "Как работает JIT компиляция в PyPy?",
            "Что такое multiprocessing vs multithreading?",
            "Как спроектировать высоконагруженное приложение на Python?",
            "Что такое контейнеризация Python-приложений?"
        ]
    },
    "Java": {
        "Junior": [
            "Что такое JVM?",
            "Чем отличается `==` от `equals()`?",
            "Что такое public static void main?",
            "Что такое конструктор?",
            "Что такое перегрузка методов?",
            "Что такое наследование?",
            "Чем отличается абстрактный класс от интерфейса?",
            "Что такое пакет (package) в Java?",
            "Какие модификаторы доступа существуют?"
        ],
        "Middle": [
            "Как работает сборщик мусора в Java?",
            "Что такое Stream API?",
            "Чем отличается synchronized от ReentrantLock?",
            "Что такое Optional?",
            "Как работает HashMap?",
            "Что такое исключения (checked vs unchecked)?",
            "Что такое generics?",
            "Что такое JPA и Hibernate?",
            "Что такое Spring Boot?"
        ],
        "Senior": [
            "Как работает загрузка классов в Java?",
            "Что такое Java Memory Model?",
            "Как оптимизировать GC?",
            "Что такое JMH?",
            "Как отлаживать многопоточные приложения?",
            "Что такое модули в Java 9+?",
            "Что такое Project Loom?",
            "Как спроектировать микросервисы на Java?",
            "Что такое реактивное программирование в Java?",
            "Как работает JIT компиляция в HotSpot?"
        ]
    },
    "SQL": {
        "Junior": [
            "Что такое JOIN?",
            "Чем отличается INNER JOIN от LEFT JOIN?",
            "Что такое JOIN?",
            "Что такое GROUP BY?",
            "Что такое ORDER BY?",
            "Что такое LIMIT?",
            "Что такое первичный ключ?",
            "Что такое внешний ключ?",
            "Что такое индекс?"
        ],
        "Middle": [
            "Что такое транзакции и ACID?",
            "Что такое оконные функции?",
            "Что такое UNION vs UNION ALL?",
            "Как работают индексы (B-Tree, Hash)?",
            "Что такое EXPLAIN?",
            "Что такое нормализация и денормализация?",
            "Чем отличается кластерный индекс от некластерного?",
            "Что такое оконные функции?",
            "Что такое CTE (Common Table Expression)?",
            "Как оптимизировать медленные запросы?"
        ],
        "Senior": [
            "Что такое шардирование и партиционирование?",
            "Что такое CAP теорема?",
            "Как настроить репликацию?",
            "Что такое CAP теорема?",
            "Как выбрать между SQL и NoSQL?",
            "Что такое MVCC?",
            "Как отлаживать deadlock?",
            "Что такое пул соединений?",
            "Как работает кэширование в БД?",
            "Что такое миграции и как их управлять?"
        ]
    },
    "Git": {
        "Junior": [
            "Что такое Git?",
            "Чем отличается git pull от git fetch?",
             "Что такое commit?",
            "Что такое branch?",
            "Как создать новую ветку?",
            "Как переключиться между ветками?",
            "Что такое merge?",
            "Что такое конфликт и как его решить?",
            "Что такое .gitignore?",
            "Как посмотреть историю коммитов?"
        ],
        "Middle": [
            "Чем отличается rebase от merge?",
            "Что такое cherry-pick?",
            "Что такое stash?",
            "Как отменить коммит?",
            "Что такое reset (soft/hard/mixed)?",
            "Что такое revert?",
            "Как работать с remote?",
            "Что такое tag?",
            "Как переписать историю (rebase -i)?",
            "Что такое Git Flow?"
        ],
        "Senior": [
            "Как настроить CI/CD с Git?",
            "Что такое Git hooks?",
            "Как работает Git под капотом? (объекты, деревья)",
            "Как восстановить удаленную ветку?",
            "Как мигрировать репозиторий из SVN в Git?",
            "Что такое Git LFS?",
            "Как автоматизировать проверки в pre-commit?",
            "Что такое Git bisect?",
            "Как управлять монорепозиторием?",
            "Какие стратегии ветвления существуют?"
        ]
    }
}

def get_topics():
    """Возвращает список доступных тем"""
    return list(QUESTIONS.keys())

def get_levels_for_topic(topic: str):
    """Возвращает список уровней для темы"""
    return list(QUESTIONS.get(topic, {}).keys())

def get_questions(topic: str, level: str):
    """Возвращает вопросы для темы и уровня"""
    return QUESTIONS.get(topic, {}).get(level, [])

def get_next_question(questions: list, index: int):
    """Возвращает следующий вопрос по индексу"""
    return questions[index] if index < len(questions) else None

async def finish_interview(state, user_id: int, total_questions: int, message=None):
    from services.stats_service import add_interview_result

    data = await state.get_data()

    total_score = data.get("total_score", 0)
    level = data.get("level", "Unknown")

    max_score = total_questions * 10
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0

    print("END OF INTERVIEW")
    print("FINAL SCORE:", total_score)

    # Сохраняем
    add_interview_result(
        user_id=user_id,
        level=level,
        total_questions=total_questions,
        total_score=total_score,
        max_score=max_score,
        answers=[]
    )

    summary = f"""
🎉 Интервью завершено! 🎉

📊 Результаты:
━━━━━━━━━━━━━━━━━━━
✅ Набрано баллов: {total_score} / {max_score}
📈 Процент: {percentage:.1f}%

💬 Оценка:
{"🌟 Отлично! Вы готовы к повышению!" if percentage >= 80 else 
"👍 Хорошо, но есть куда расти" if percentage >= 60 else
"📚 Рекомендуем подтянуть теорию"}
━━━━━━━━━━━━━━━━━━━

Спасибо за участие! 
/start для новой попытки
/stats для просмотра статистики
"""

    if message:
        await message.answer(
            summary,
            reply_markup=ReplyKeyboardRemove())

    await state.clear()