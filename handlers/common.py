from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

from config import LANGUAGES

router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start."""
    await state.update_data(language="ru")
    await show_main_menu(message, state)


async def show_main_menu(message: Message, state: FSMContext) -> None:
    """Отображает главное меню бота."""
    user_data = await state.get_data()
    language = user_data.get("language", "ru")

    kb = [
        [KeyboardButton(text="📝 Написать отчет" if language == "ru" else
                        "📝 Write a report" if language == "en" else
                        "📝 Scrivi un rapporto" if language == "it" else
                        "📝 Bericht schreiben")],
        [KeyboardButton(text="🙏 Поблагодарить разработчика" if language == "ru" else
                        "🙏 Thank the developer" if language == "en" else
                        "🙏 Ringrazia lo sviluppatore" if language == "it" else
                        "🙏 Danke dem Entwickler")],
        [KeyboardButton(text="🌍 Изменить язык" if language == "ru" else
                        "🌍 Change language" if language == "en" else
                        "🌍 Cambia lingua" if language == "it" else
                        "🌍 Sprache ändern")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply(
        "Выберите действие:" if language == "ru" else
        "Choose an action:" if language == "en" else
        "Scegli un'azione:" if language == "it" else
        "Wählen Sie eine Aktion:", reply_markup=keyboard)


@router.message(lambda message: message.text in [
    "🙏 Поблагодарить разработчика", "🙏 Thank the developer", "🙏 Ringrazia lo sviluppatore", "🙏 Danke dem Entwickler"
])
async def thank_developer(message: Message) -> None:
    """Обработчик кнопки благодарности разработчику."""
    await message.reply(
        "Спасибо! 😊" if message.text == "🙏 Поблагодарить разработчика" else
        "Thank you! 😊" if message.text == "🙏 Thank the developer" else
        "Grazie! 😊" if message.text == "🙏 Ringrazia lo sviluppatore" else
        "Danke! 😊") 