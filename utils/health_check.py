import logging

logger = logging.getLogger(__name__)

async def check_bot_health(bot) -> dict:
    """
    Проверяет здоровье бота
    Возвращает словарь со статусами
    """
    health_status = {
        "bot_running": False,
        "webhook_set": False,
        "error": None
    }
    
    try:
        # Проверяем, отвечает ли бот
        bot_info = await bot.get_me()
        health_status["bot_running"] = True
        health_status["bot_name"] = bot_info.full_name
        health_status["bot_username"] = bot_info.username
        
        # Проверяем вебхук (если используется)
        webhook_info = await bot.get_webhook_info()
        health_status["webhook_set"] = bool(webhook_info.url)
        
    except Exception as e:
        health_status["error"] = str(e)
        logger.error(f"Health check failed: {e}")
    
    return health_status


def format_health_message(health_data: dict) -> str:
    """Форматирует сообщение о здоровье бота"""
    if health_data.get("error"):
        return f"❌ Бот не работает: {health_data['error']}"
    
    status_emoji = "✅" if health_data["bot_running"] else "❌"
    webhook_emoji = "🔗" if health_data.get("webhook_set") else "📡"
    
    message = f"{status_emoji} *Статус бота:*\n"
    message += f"Имя: {health_data.get('bot_name', 'Unknown')}\n"
    message += f"Username: @{health_data.get('bot_username', 'unknown')}\n"
    message += f"{webhook_emoji} Webhook: {'включен' if health_data.get('webhook_set') else 'выключен (polling)'}\n"
    message += f"\n🟢 Бот работает в штатном режиме"
    
    return message