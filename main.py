import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import common, report, settings

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(common.router)
dp.include_router(report.router)
dp.include_router(settings.router)


async def main():
    """Основная функция запуска бота."""
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())