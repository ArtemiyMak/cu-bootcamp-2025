import asyncio
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
import requests

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

dp = Dispatcher()
bot = Bot(token=bot_token)


class ReportInfo(StatesGroup):
    waiting_for_date = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()
    waiting_for_student_name = State()
    waiting_for_student_age = State()
    waiting_for_lesson_topic = State()
    waiting_for_homework = State()
    waiting_for_feedback = State()
    waiting_for_comment = State()


parameters = [
    ("Дата урока", ReportInfo.waiting_for_date),
    ("Время начала урока", ReportInfo.waiting_for_start_time),
    ("Время окончания урока", ReportInfo.waiting_for_end_time),
    ("Имя ученика", ReportInfo.waiting_for_student_name),
    ("Возраст ученика", ReportInfo.waiting_for_student_age),
    ("Тема урока", ReportInfo.waiting_for_lesson_topic),
    ("Домашнее задание", ReportInfo.waiting_for_homework),
    ("Обратная связь от ученика", ReportInfo.waiting_for_feedback),
    ("Общий комментарий репетитора", ReportInfo.waiting_for_comment),
]


def report_gen(params, answers):
    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    gpt_model = 'yandexgpt-lite'
    system_prompt = (
        "Придумай цельный отчет. Без дополнительного оформления, цельным текстом. Далее будут даны параметры и ответы на них, "
        "напиши связный цельный текст, описывающий прошедший урок, будь креативным, развернуто используй данные параметры и ответы "
        "для создания человекоподобного текста."
    )
    user_prompt = (
        "Параметры для отчета:\n" + "\n".join(params) + "\n\nОтветы:\n" + "\n".join(answers))
    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 1, 'maxTokens': 5000},
        'messages': [
            {'role': 'system', 'text': system_prompt},
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


@dp.message(Command("start"))
async def start(message: Message) -> None:
    kb = [
        [KeyboardButton(text="Написать отчет")],
        [KeyboardButton(text="Поблагодарить разработчика")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Выберите действие:", reply_markup=keyboard)


async def ask_next_parameter(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    current_step = user_data.get("current_step", 0)

    if current_step < len(parameters):
        parameter_name, next_state = parameters[current_step]
        await message.reply(f"Введите {parameter_name}:")
        await state.set_state(next_state)
        await state.update_data(current_step=current_step + 1)
    else:
        await finish_report(message, state)


@dp.message(ReportInfo.waiting_for_date)
async def process_date(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_start_time)
async def process_start_time(message: Message, state: FSMContext) -> None:
    await state.update_data(start_time=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_end_time)
async def process_end_time(message: Message, state: FSMContext) -> None:
    await state.update_data(end_time=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_student_name)
async def process_student_name(message: Message, state: FSMContext) -> None:
    await state.update_data(student_name=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_student_age)
async def process_student_age(message: Message, state: FSMContext) -> None:
    await state.update_data(student_age=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_lesson_topic)
async def process_lesson_topic(message: Message, state: FSMContext) -> None:
    await state.update_data(lesson_topic=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_homework)
async def process_homework(message: Message, state: FSMContext) -> None:
    await state.update_data(homework=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext) -> None:
    await state.update_data(feedback=message.text)
    await ask_next_parameter(message, state)


@dp.message(ReportInfo.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=message.text)
    await ask_next_parameter(message, state)


async def finish_report(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    await state.clear()

    collected_parameters = []
    collected_answers = []

    if "date" in user_data:
        collected_parameters.append("Дата урока")
        collected_answers.append(user_data["date"])
    if "start_time" in user_data:
        collected_parameters.append("Время начала урока")
        collected_answers.append(user_data["start_time"])
    if "end_time" in user_data:
        collected_parameters.append("Время окончания урока")
        collected_answers.append(user_data["end_time"])
    if "student_name" in user_data:
        collected_parameters.append("Имя ученика")
        collected_answers.append(user_data["student_name"])
    if "student_age" in user_data:
        collected_parameters.append("Возраст ученика")
        collected_answers.append(user_data["student_age"])
    if "lesson_topic" in user_data:
        collected_parameters.append("Тема урока")
        collected_answers.append(user_data["lesson_topic"])
    if "homework" in user_data:
        collected_parameters.append("Домашнее задание")
        collected_answers.append(user_data["homework"])
    if "feedback" in user_data:
        collected_parameters.append("Обратная связь от ученика")
        collected_answers.append(user_data["feedback"])
    if "comment" in user_data:
        collected_parameters.append("Общий комментарий репетитора")
        collected_answers.append(user_data["comment"])

    report = report_gen(collected_parameters, collected_answers)
    await message.reply("Отчет сформирован:\n\n" + report)

    kb = [
        [KeyboardButton(text="Написать отчет")],
        [KeyboardButton(text="Поблагодарить разработчика")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Выберите действие:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "Написать отчет")
async def start_report(message: Message, state: FSMContext) -> None:
    await state.update_data(current_step=0)
    await ask_next_parameter(message, state)


@dp.message(lambda message: message.text == "Поблагодарить разработчика")
async def thank_developer(message: Message) -> None:
    await message.reply("Спасибо!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
