import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config import load_config
from app.handlers.drinks import register_handlers_drinks
from app.handlers.food import register_handlers_food
from app.handlers.common import register_handlers_common
from app.handlers.today import register_handlers_today
from app.handlers.calendar import register_handlers_calendar
from app.handlers.view import register_handlers_view
from app.handlers.diagram import register_handlers_diagram

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/today", description="Настроение на сегодня 🙂"),
        BotCommand(command="/calendar", description="Календарь 📆"),
        BotCommand(command="/diagram", description="Просмотр графика 📊"),
        BotCommand(command="/view", description="Просмотр записей 📖"),
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Парсинг файла конфигурации
    config = load_config("config/bot.ini")

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp, config.tg_bot.admin_id)
    register_handlers_drinks(dp)
    register_handlers_food(dp)
    register_handlers_today(dp)
    register_handlers_calendar(dp)
    register_handlers_view(dp)
    register_handlers_diagram(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())