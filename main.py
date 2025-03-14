import asyncio
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv
import requests

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

dp = Dispatcher()
bot = Bot(token=bot_token)


class ReportInfo(StatesGroup):
    waiting_for_answers = State()

def report_gen(parameters, answers):
    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    gpt_model = 'yandexgpt-lite'
    system_prompt = "Придумай цельный отчет. Без дополнительного оформления, цельным текстом. Далее будут даны параметры и ответы на них, напиши связный цельный текст, описывающий прошедший урок, будь креативным, развернуто используй данные параметры и ответы для создания человекоподобного текста."
    user_prompt = (
            "Параметры для отчета:\n" + "\n".join(parameters) + "\n\n"
                                                                "Ответы:\n" + "\n".join(answers)
    )
    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 1, 'maxTokens': 5000},
        'messages': [
            {'role': 'system', 'text': system_prompt},  # Системный промпт
            {'role': 'user', 'text': user_prompt},
        ],
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {api_key}'
    }
    response = requests.post(url, headers=headers, json=body)
    operation_id = response.json().get('id')
    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}
    while True:
        response = requests.get(url, headers=headers)
        done = response.json()["done"]
        if done:
            break
        time.sleep(2)
    data = response.json()
    answer = data['response']['alternatives'][0]['message']['text']
    return answer
parameters = [
    "1. Дата урока",
    "2. Время начала",
    "3. Время окончания",
    "4. Продолжительность урока",
    "5. Имя ученика",
    "6. Возраст ученика",
    "7. Уровень знаний",
    "8. Тематика урока",
    "9. Цели урока",
    "10. Методы обучения",
    "11. Используемые материалы",
    "12. Активность ученика",
    "13. Проблемные области",
    "14. Домашнее задание",
    "15. Обратная связь от ученика",
    "16. Обратная связь от родителей",
    "17. Рекомендации для следующего урока",
    "18. Оценка урока",
    "19. Общее впечатление",
    "20. Дополнительные комментарии"
]


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext) -> None:
    kb = [
        [KeyboardButton(text="Написать отчет")],
        [KeyboardButton(text="Поблагодарить разработчика")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Выберите действие:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "Написать отчет")
async def start_report(message: Message, state: FSMContext) -> None:

    parameters_list = "\n".join(parameters)

    await message.reply(f"Заполни параметры для отчета. Вот параметры, которые могут быть в него включены:\n{parameters_list}\n\nОтправь ответ в виде: 1) ответ1 2) ответ2 ...", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ReportInfo.waiting_for_answers)


@dp.message(lambda message: message.text == "Поблагодарить разработчика")
async def thank_developer(message: Message) -> None:
    await message.reply("Спасибо!")


@dp.message(ReportInfo.waiting_for_answers)
async def process_answer(message: Message, state: FSMContext) -> None:
    user_answers = message.text
    await message.reply(report_gen(parameters, user_answers))
    await state.clear()
    kb = [
        [KeyboardButton(text="Написать отчет")],
        [KeyboardButton(text="Поблагодарить разработчика")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Выберите действие:", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())