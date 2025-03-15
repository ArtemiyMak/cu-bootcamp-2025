import asyncio
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
from openai import OpenAI
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


class UserSettings(StatesGroup):
    waiting_for_language = State()


# Language-specific texts
LANGUAGES = {
    "ru": {"flag": "🇷🇺", "name": "Русский"},
    "en": {"flag": "🇬🇧", "name": "English"},
    "it": {"flag": "🇮🇹", "name": "Italiano"},
    "de": {"flag": "🇩🇪", "name": "Deutsch"},
}

parameters = [
    ("Дата урока", "Lesson date", "Data della lezione", "Datum der Stunde", ReportInfo.waiting_for_date),
    ("Время начала урока", "Lesson start time", "Ora di inizio della lezione", "Startzeit der Stunde", ReportInfo.waiting_for_start_time),
    ("Время окончания урока", "Lesson end time", "Ora di fine della lezione", "Endzeit der Stunde", ReportInfo.waiting_for_end_time),
    ("Имя ученика", "Student name", "Nome dello studente", "Name des Schülers", ReportInfo.waiting_for_student_name),
    ("Возраст ученика", "Student age", "Età dello studente", "Alter des Schülers", ReportInfo.waiting_for_student_age),
    ("Тема урока", "Lesson topic", "Argomento della lezione", "Thema der Stunde", ReportInfo.waiting_for_lesson_topic),
    ("Домашнее задание", "Homework", "Compiti a casa", "Hausaufgaben", ReportInfo.waiting_for_homework),
    ("Обратная связь от ученика", "Student feedback", "Feedback dello studente", "Feedback des Schülers", ReportInfo.waiting_for_feedback),
    ("Общий комментарий репетитора", "Tutor's comment", "Commento del tutor", "Kommentar des Tutors", ReportInfo.waiting_for_comment),
]


def report_gen(params, answers, language):
    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    gpt_model = 'yandexgpt-lite'

    system_prompt = (
        "Придумай цельный отчет. Без дополнительного оформления, цельным текстом. Далее будут даны параметры и ответы на них, "
        "напиши связный цельный текст, описывающий прошедший урок, будь креативным, развернуто используй данные параметры и ответы "
        "для создания человекоподобного текста." if language == "ru" else
        "Create a comprehensive report. Without additional formatting, as a continuous text. Below will be given parameters and answers to them, "
        "write a coherent and comprehensive text describing the past lesson in detail. Be creative and use the provided parameters and answers extensively. "
        "Include specific examples, elaborate on key points, and provide a thorough analysis of the lesson. Ensure the text is engaging, informative, and human-like, "
        "with a natural flow and a length that is approximately 1.5 to 2 times longer than usual. USE ONLY ENGLISH LANGUAGE STRICTLY" if language == "en" else
        "Crea un rapporto completo. Senza formattazione aggiuntiva, come testo continuo. Di seguito verranno forniti parametri e risposte, "
        "scrivi un testo coerente e completo che descriva la lezione passata in dettaglio. Sii creativo e utilizza i parametri e le risposte fornite in modo esteso. "
        "Includi esempi specifici, approfondisci i punti chiave e fornisci un'analisi approfondita della lezione. Assicurati che il testo sia coinvolgente, informativo e simile a quello umano, "
        "con un flusso naturale e una lunghezza approssimativamente 1,5-2 volte maggiore del solito. UTILIZZARE ESCLUSIVAMENTE LA LINGUA ITALIANA " if language == "it" else
        "Erstelle einen umfassenden Bericht. Ohne zusätzliche Formatierung, als fortlaufender Text. Es werden Parameter und Antworten darauf gegeben, "
        "schreibe einen zusammenhängenden und umfassenden Text, der die vergangene Stunde detailliert beschreibt. Sei kreativ und verwende die bereitgestellten Parameter und Antworten ausführlich. "
        "Füge spezifische Beispiele hinzu, gehe auf Schlüsselpunkte ein und liefere eine gründliche Analyse der Stunde. Achte darauf, dass der Text ansprechend, informativ und menschenähnlich ist, "
        "mit einem natürlichen Fluss und einer Länge, die etwa 1,5- bis 2-mal länger ist als üblich. VERWENDEN SIE AUSSCHLIESSLICH DIE DEUTSCHE SPRACHE"
    )

    user_prompt = (
        "Параметры для отчета:\n" + "\n".join(params) + "\n\nОтветы:\n" + "\n".join(answers) if language == "ru" else
        "Parameters for the report:\n" + "\n".join(params) + "\n\nAnswers:\n" + "\n".join(answers) if language == "en" else
        "Parametri per il rapporto:\n" + "\n".join(params) + "\n\nRisposte:\n" + "\n".join(answers) if language == "it" else
        "Parameter für den Bericht:\n" + "\n".join(params) + "\n\nAntworten:\n" + "\n".join(answers)
    )

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


def report_gen_gpt(params, answers, language):
    base_url = "https://api.aimlapi.com/v1"
    api_key = "028b03024e454ea1a156d289a7003dce" ##FIX THIS SHIT
    system_prompt = (
        "детальный отчет по русски параметры:дата урока,время начала/конца,имя/возраст студента,тема,ДЗ,отзыв ученика,комм. репет." if language == "ru" else
        "detailed report in English.Use:Lesson date,start/end time,student name/age,topic,homework,feedback,tutor commentif language" == "en" if language == "en" else
        "un rapporto dettagliato in italiano.Usa:data lezione,ora inizio/fine,nome/età studente,argomento,compiti,feedback,commento tutor" if language == "it" else
        "Erstelle detaillierten Bericht auf Deutsch.Nutze:Datum, Start / Ende, Name / Alter, Thema, Hausaufgaben, Feedback, Kommentar."
    )

    user_prompt = (
        "\n\nОтветы:\n" + "\n".join(answers) if language == "ru" else
        "\n\nAnswers:\n" + "\n".join(answers) if language == "en" else
        "\n\nRisposte:\n" + "\n".join(answers) if language == "it" else
        "\n\nAntworten:\n" + "\n".join(answers)
    )
    print(system_prompt)
    print(user_prompt)
    api = OpenAI(api_key=api_key, base_url=base_url)
    completion = api.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=256,
    )

    response = completion.choices[0].message.content
    return response

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext) -> None:
    await state.update_data(language="ru")
    await show_main_menu(message, state)


async def show_main_menu(message: Message, state: FSMContext) -> None:
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


@dp.message(lambda message: message.text in [
    "📝 Написать отчет", "📝 Write a report", "📝 Scrivi un rapporto", "📝 Bericht schreiben"
])
async def start_report(message: Message, state: FSMContext) -> None:
    await state.update_data(current_step=0)
    await ask_next_parameter(message, state)


async def ask_next_parameter(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    current_step = user_data.get("current_step", 0)
    language = user_data.get("language", "ru")

    if current_step < len(parameters):
        parameter_name_ru, parameter_name_en, parameter_name_it, parameter_name_de, next_state = parameters[current_step]
        parameter_name = (
            parameter_name_ru if language == "ru" else
            parameter_name_en if language == "en" else
            parameter_name_it if language == "it" else
            parameter_name_de
        )
        await message.reply(
            f"Введите {parameter_name}:" if language == "ru" else
            f"Enter {parameter_name}:" if language == "en" else
            f"Inserisci {parameter_name}:" if language == "it" else
            f"Geben Sie {parameter_name} ein:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True))
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
        collected_parameters.append("Дата урока" if user_data.get("language") == "ru" else
                                   "Lesson date" if user_data.get("language") == "en" else
                                   "Data della lezione" if user_data.get("language") == "it" else
                                   "Datum der Stunde")
        collected_answers.append(user_data["date"])
    if "start_time" in user_data:
        collected_parameters.append("Время начала урока" if user_data.get("language") == "ru" else
                                   "Lesson start time" if user_data.get("language") == "en" else
                                   "Ora di inizio della lezione" if user_data.get("language") == "it" else
                                   "Startzeit der Stunde")
        collected_answers.append(user_data["start_time"])
    if "end_time" in user_data:
        collected_parameters.append("Время окончания урока" if user_data.get("language") == "ru" else
                                   "Lesson end time" if user_data.get("language") == "en" else
                                   "Ora di fine della lezione" if user_data.get("language") == "it" else
                                   "Endzeit der Stunde")
        collected_answers.append(user_data["end_time"])
    if "student_name" in user_data:
        collected_parameters.append("Имя ученика" if user_data.get("language") == "ru" else
                                   "Student name" if user_data.get("language") == "en" else
                                   "Nome dello studente" if user_data.get("language") == "it" else
                                   "Name des Schülers")
        collected_answers.append(user_data["student_name"])
    if "student_age" in user_data:
        collected_parameters.append("Возраст ученика" if user_data.get("language") == "ru" else
                                   "Student age" if user_data.get("language") == "en" else
                                   "Età dello studente" if user_data.get("language") == "it" else
                                   "Alter des Schülers")
        collected_answers.append(user_data["student_age"])
    if "lesson_topic" in user_data:
        collected_parameters.append("Тема урока" if user_data.get("language") == "ru" else
                                   "Lesson topic" if user_data.get("language") == "en" else
                                   "Argomento della lezione" if user_data.get("language") == "it" else
                                   "Thema der Stunde")
        collected_answers.append(user_data["lesson_topic"])
    if "homework" in user_data:
        collected_parameters.append("Домашнее задание" if user_data.get("language") == "ru" else
                                   "Homework" if user_data.get("language") == "en" else
                                   "Compiti a casa" if user_data.get("language") == "it" else
                                   "Hausaufgaben")
        collected_answers.append(user_data["homework"])
    if "feedback" in user_data:
        collected_parameters.append("Обратная связь от ученика" if user_data.get("language") == "ru" else
                                   "Student feedback" if user_data.get("language") == "en" else
                                   "Feedback dello studente" if user_data.get("language") == "it" else
                                   "Feedback des Schülers")
        collected_answers.append(user_data["feedback"])
    if "comment" in user_data:
        collected_parameters.append("Общий комментарий репетитора" if user_data.get("language") == "ru" else
                                   "Tutor's comment" if user_data.get("language") == "en" else
                                   "Commento del tutor" if user_data.get("language") == "it" else
                                   "Kommentar des Tutors")
        collected_answers.append(user_data["comment"])

    report = report_gen_gpt(collected_parameters, collected_answers, user_data.get("language", "ru"))
    await message.reply(
        "📄 Отчет сформирован:\n\n" + report if user_data.get("language") == "ru" else
        "📄 Report generated:\n\n" + report if user_data.get("language") == "en" else
        "📄 Rapporto generato:\n\n" + report if user_data.get("language") == "it" else
        "📄 Bericht erstellt:\n\n" + report)

    await show_main_menu(message, state)


@dp.message(lambda message: message.text in [
    "🙏 Поблагодарить разработчика", "🙏 Thank the developer", "🙏 Ringrazia lo sviluppatore", "🙏 Danke dem Entwickler"
])
async def thank_developer(message: Message) -> None:
    await message.reply(
        "Спасибо! 😊" if message.text == "🙏 Поблагодарить разработчика" else
        "Thank you! 😊" if message.text == "🙏 Thank the developer" else
        "Grazie! 😊" if message.text == "🙏 Ringrazia lo sviluppatore" else
        "Danke! 😊")


@dp.message(lambda message: message.text in [
    "🌍 Изменить язык", "🌍 Change language", "🌍 Cambia lingua", "🌍 Sprache ändern"
])
async def change_language(message: Message, state: FSMContext) -> None:
    kb = [
        [KeyboardButton(text=f"{LANGUAGES['ru']['flag']} {LANGUAGES['ru']['name']}")],
        [KeyboardButton(text=f"{LANGUAGES['en']['flag']} {LANGUAGES['en']['name']}")],
        [KeyboardButton(text=f"{LANGUAGES['it']['flag']} {LANGUAGES['it']['name']}")],
        [KeyboardButton(text=f"{LANGUAGES['de']['flag']} {LANGUAGES['de']['name']}")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Выберите язык / Choose language / Scegli la lingua / Wählen Sie die Sprache:", reply_markup=keyboard)
    await state.set_state(UserSettings.waiting_for_language)


@dp.message(UserSettings.waiting_for_language)
async def process_language_change(message: Message, state: FSMContext) -> None:
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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())