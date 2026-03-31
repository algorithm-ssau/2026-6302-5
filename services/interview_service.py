QUESTIONS = {
    "Junior": [
        "Что такое Dependency Injection?",
        "Что такое REST API?",
        "Чем отличается GET от POST?",
        "Что такое ООП? Назовите 3 принципа.",
        "Что такое SQL инъекция? Как защититься?",
        "Чем отличается List от Set в Java/Python?",
        "Что такое Git и зачем он нужен?",
        "Что такое JWT токен?",
        "Что такое Docker?",
        "Чем отличается HTTP от HTTPS?"
    ],
    "Middle": [
        "Как работает Spring Boot Auto Configuration?",
        "Что такое транзакции? ACID?",
        "Как работает сборщик мусора в Java/Python?",
        "Что такое индексы в БД? Когда использовать?",
        "Чем отличается JOIN от LEFT JOIN?",
        "Что такое Redis и для чего используют?",
        "Как работает JWT верификация?",
        "Что такое многопоточность? Проблемы?",
        "Что такое SOLID? Назовите каждый принцип.",
        "Как отличить N+1 проблему в ORM?"
    ],
    "Senior": [
        "Что такое CAP theorem?",
        "Как спроектировать high-load систему?",
        "Что такое Event Sourcing?",
        "Что такое CQRS?",
        "Как обеспечить согласованность данных в микросервисах?",
        "Что такое Circuit Breaker?",
        "Как бы вы мигрировали монолит в микросервисы?",
        "Что такое Sharding и партиционирование?",
        "Как отлаживать продакшен падение производительности?",
        "Что такое RAFT или Paxos?"
    ]
}

def get_questions(level):
    return QUESTIONS.get(level, [])

def get_next_question(questions, index):
    return questions[index] if index < len(questions) else None