import json
import os
from datetime import datetime
from typing import Dict, List

DATA_FILE = "data/stats.json"


def load_stats(user_id: int) -> Dict:
    """Загружает статистику пользователя"""
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_stats = json.load(f)

    return all_stats.get(str(user_id), {})


def save_stats(user_id: int, stats: Dict):
    """Сохраняет статистику пользователя"""

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    all_stats = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_stats = json.load(f)

    all_stats[str(user_id)] = stats

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)


def add_interview_result(
        user_id: int,
        level: str,
        total_questions: int,
        total_score: int,
        max_score: int,
        answers: List[Dict]
):
    print("🔥 ADD INTERVIEW CALLED")
    stats = load_stats(user_id)

    if "interviews" not in stats:
        stats["interviews"] = []

    stats["interviews"].append({
        "id": len(stats["interviews"]) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "total_questions": total_questions,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": round((total_score / max_score) * 100, 1),
        "answers": answers
    })

    if len(stats["interviews"]) > 10:
        stats["interviews"] = stats["interviews"][-10:]

    save_stats(user_id, stats)
