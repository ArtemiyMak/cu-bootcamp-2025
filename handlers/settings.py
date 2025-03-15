from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

from config import LANGUAGES
from handlers.common import show_main_menu
from states import UserSettings

router = Router()

@router.message(lambda message: message.text in [
    "🌍 Изменить язык", "🌍 Change language", "🌍 Cambia lingua", "🌍 Sprache ändern"
])
async def change_language(message: Message, state: FSMContext) -> None:
    """Обработчик кнопки изменения языка."""
    kb = [
        [KeyboardButton(text=f"{LANGUAGES['ru']['flag']} {LANGUAGES['ru']['name']}")],
        [KeyboardButton(text=f"{LANGUAGES['en']['flag']} {LANGUAGES['en']['name']}")],
        [KeyboardButton(text=f"{LANGUAGES['it']['flag']} {LANGUAGES['it']['name']}")],
        [KeyboardButton(text=f"{LANGUAGES['de']['flag']} {LANGUAGES['de']['name']}")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Выберите язык / Choose language / Scegli la lingua / Wählen Sie die Sprache:", reply_markup=keyboard)
    await state.set_state(UserSettings.waiting_for_language)


@router.message(UserSettings.waiting_for_language)
async def process_language_change(message: Message, state: FSMContext) -> None:
    """Обработчик выбора языка."""
    language_map = {
        f"{LANGUAGES['ru']['flag']} {LANGUAGES['ru']['name']}": "ru",
        f"{LANGUAGES['en']['flag']} {LANGUAGES['en']['name']}": "en",
        f"{LANGUAGES['it']['flag']} {LANGUAGES['it']['name']}": "it",
        f"{LANGUAGES['de']['flag']} {LANGUAGES['de']['name']}": "de",
    }

    if message.text not in language_map:
        await message.reply("Пожалуйста, выберите язык из предложенных. / Please choose a language from the options.")
        return

    selected_language = language_map[message.text]
    await state.update_data(language=selected_language)
    await message.reply(
        "✅ Язык изменен. / Language changed. / Lingua cambiata. / Sprache geändert.")
    await show_main_menu(message, state) 