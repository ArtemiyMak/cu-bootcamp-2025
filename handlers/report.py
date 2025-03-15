from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import time

from config import REPORT_PARAMETERS
from handlers.common import show_main_menu
from report_generator import report_gen, report_gen_gpt
from states import ReportInfo

router = Router()

@router.message(lambda message: message.text in [
    "📝 Написать отчет", "📝 Write a report", "📝 Scrivi un rapporto", "📝 Bericht schreiben"
])
async def start_report(message: Message, state: FSMContext) -> None:
    """Начало создания отчета."""
    # Сбрасываем все данные, кроме языка
    language = (await state.get_data()).get("language", "ru")
    await state.clear()
    await state.update_data(current_step=0, answers={}, language=language)
    await ask_next_parameter(message, state)


async def ask_next_parameter(message: Message, state: FSMContext) -> None:
    """Запрашивает следующий параметр для отчета."""
    user_data = await state.get_data()
    current_step = user_data.get("current_step", 0)
    language = user_data.get("language", "ru")

    if current_step < len(REPORT_PARAMETERS):
        parameter_name_ru, parameter_name_en, parameter_name_it, parameter_name_de, state_name = REPORT_PARAMETERS[current_step]
        parameter_name = (
            parameter_name_ru if language == "ru" else
            parameter_name_en if language == "en" else
            parameter_name_it if language == "it" else
            parameter_name_de
        )
        
        # Основные примеры для каждого параметра
        example_texts = {
            "ru": [
                "15.03.2024",  # Дата
                "18:00",       # Время начала
                "19:00",       # Время окончания
                "Алексей",     # Имя ученика
                "12",          # Возраст
                "Математика: дроби",  # Тема
                "Решить задачи 1-5 на странице 42",  # ДЗ
                "Понравилось, было интересно",  # Отзыв
                "Хорошо усваивает материал"  # Комментарий
            ],
            "en": [
                "15.03.2024",
                "6:00 PM",
                "7:00 PM",
                "Alex",
                "12",
                "Math: fractions",
                "Solve problems 1-5 on page 42",
                "Enjoyed it, was interesting",
                "Understands the material well"
            ],
            "it": [
                "15.03.2024",
                "18:00",
                "19:00",
                "Alessandro",
                "12",
                "Matematica: frazioni",
                "Risolvere i problemi 1-5 a pagina 42",
                "È piaciuto, è stato interessante",
                "Comprende bene il materiale"
            ],
            "de": [
                "15.03.2024",
                "18:00",
                "19:00",
                "Alexander",
                "12",
                "Mathematik: Brüche",
                "Löse Aufgaben 1-5 auf Seite 42",
                "Hat Spaß gemacht, war interessant",
                "Versteht das Material gut"
            ]
        }
        
        # Альтернативные примеры для разнообразия
        alt_example_texts = {
            "ru": [
                "20.03.2024",  # Дата
                "15:30",       # Время начала
                "16:30",       # Время окончания
                "Мария",       # Имя ученика
                "14",          # Возраст
                "Английский: неправильные глаголы",  # Тема
                "Выучить 20 неправильных глаголов и составить с ними предложения",  # ДЗ
                "Было сложно, но интересно. Хочу продолжить изучение темы",  # Отзыв
                "Ученица старается, проявляет интерес к языку"  # Комментарий
            ],
            "en": [
                "20.03.2024",
                "3:30 PM",
                "4:30 PM",
                "Mary",
                "14",
                "English: irregular verbs",
                "Learn 20 irregular verbs and make sentences with them",
                "It was challenging but interesting. Want to continue learning the topic",
                "The student tries hard and shows interest in the language"
            ],
            "it": [
                "20.03.2024",
                "15:30",
                "16:30",
                "Maria",
                "14",
                "Inglese: verbi irregolari",
                "Imparare 20 verbi irregolari e creare frasi con essi",
                "È stato difficile ma interessante. Voglio continuare a studiare l'argomento",
                "La studentessa si impegna e mostra interesse per la lingua"
            ],
            "de": [
                "20.03.2024",
                "15:30",
                "16:30",
                "Maria",
                "14",
                "Englisch: unregelmäßige Verben",
                "Lerne 20 unregelmäßige Verben und bilde Sätze mit ihnen",
                "Es war schwierig, aber interessant. Ich möchte das Thema weiterhin studieren",
                "Die Schülerin strengt sich an und zeigt Interesse an der Sprache"
            ]
        }
        
        # Получаем примеры для текущего шага
        example1 = example_texts[language][current_step]
        example2 = alt_example_texts[language][current_step]
        
        # Тексты для кнопок примеров
        example1_button_text = (
            f"📤 Пример: {example1}" if language == "ru" else
            f"📤 Example: {example1}" if language == "en" else
            f"📤 Esempio: {example1}" if language == "it" else
            f"📤 Beispiel: {example1}"
        )
        
        example2_button_text = (
            f"📤 Пример 2: {example2}" if language == "ru" else
            f"📤 Example 2: {example2}" if language == "en" else
            f"📤 Esempio 2: {example2}" if language == "it" else
            f"📤 Beispiel 2: {example2}"
        )
        
        # Создаем клавиатуру с кнопками примеров и "Назад"
        back_button_text = (
            "⬅️ Назад" if language == "ru" else
            "⬅️ Back" if language == "en" else
            "⬅️ Indietro" if language == "it" else
            "⬅️ Zurück"
        )
        kb = [
            [KeyboardButton(text=example1_button_text)],
            [KeyboardButton(text=example2_button_text)],
            [KeyboardButton(text=back_button_text)]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        
        # Сохраняем текущее состояние и примеры в данных состояния
        await state.update_data(
            current_state=state_name, 
            current_example=example1,
            current_example2=example2,
            example1_button=example1_button_text,
            example2_button=example2_button_text
        )
        
        await message.reply(
            f"Введите {parameter_name}:" if language == "ru" else
            f"Enter {parameter_name}:" if language == "en" else
            f"Inserisci {parameter_name}:" if language == "it" else
            f"Geben Sie {parameter_name} ein:", reply_markup=keyboard)
        
        # Устанавливаем состояние на основе имени состояния из параметров
        state_attr = getattr(ReportInfo, state_name)
        await state.set_state(state_attr)
    else:
        await finish_report(message, state)


# Обработчик кнопки "Назад"
@router.message(lambda message: message.text in [
    "⬅️ Назад", "⬅️ Back", "⬅️ Indietro", "⬅️ Zurück"
])
async def go_back(message: Message, state: FSMContext) -> None:
    """Обработчик нажатия кнопки Назад при заполнении отчета."""
    user_data = await state.get_data()
    current_step = user_data.get("current_step", 0)
    
    # Если мы уже на первом шаге, то возвращаемся в главное меню
    if current_step <= 1:
        await state.clear()
        await show_main_menu(message, state)
        return
    
    # Иначе возвращаемся к предыдущему параметру
    await state.update_data(current_step=current_step - 1)
    await ask_next_parameter(message, state)


# Обработчики для каждого состояния
@router.message(ReportInfo.waiting_for_date)
async def process_date(message: Message, state: FSMContext) -> None:
    """Обработчик ввода даты урока."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["date"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_start_time)
async def process_start_time(message: Message, state: FSMContext) -> None:
    """Обработчик ввода времени начала урока."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["start_time"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_end_time)
async def process_end_time(message: Message, state: FSMContext) -> None:
    """Обработчик ввода времени окончания урока."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["end_time"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_student_name)
async def process_student_name(message: Message, state: FSMContext) -> None:
    """Обработчик ввода имени ученика."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["student_name"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_student_age)
async def process_student_age(message: Message, state: FSMContext) -> None:
    """Обработчик ввода возраста ученика."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["student_age"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_lesson_topic)
async def process_lesson_topic(message: Message, state: FSMContext) -> None:
    """Обработчик ввода темы урока."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["lesson_topic"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_homework)
async def process_homework(message: Message, state: FSMContext) -> None:
    """Обработчик ввода домашнего задания."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["homework"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext) -> None:
    """Обработчик ввода обратной связи."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["feedback"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


@router.message(ReportInfo.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext) -> None:
    """Обработчик ввода комментария репетитора."""
    user_data = await state.get_data()
    answers = user_data.get("answers", {})
    answers["comment"] = message.text
    await state.update_data(answers=answers)
    await state.update_data(current_step=user_data.get("current_step", 0) + 1)
    await ask_next_parameter(message, state)


# Обработчик кнопок примеров
@router.message(lambda message: message.text and (
    message.text.startswith("📤 Пример:") or 
    message.text.startswith("📤 Example:") or 
    message.text.startswith("📤 Esempio:") or 
    message.text.startswith("📤 Beispiel:") or
    message.text.startswith("📤 Пример 2:") or 
    message.text.startswith("📤 Example 2:") or 
    message.text.startswith("📤 Esempio 2:") or 
    message.text.startswith("📤 Beispiel 2:")
))
async def send_example(message: Message, state: FSMContext) -> None:
    """Обработчик нажатия кнопки с примером при заполнении отчета."""
    user_data = await state.get_data()
    language = user_data.get("language", "ru")
    current_state = user_data.get("current_state", "")
    current_step = user_data.get("current_step", 0)
    
    # Определяем, какой пример был выбран
    button_text = message.text
    example_to_use = None
    
    # Проверяем, какая кнопка была нажата
    if button_text == user_data.get("example1_button", ""):
        example_to_use = user_data.get("current_example", "")
    elif button_text == user_data.get("example2_button", ""):
        example_to_use = user_data.get("current_example2", "")
    else:
        # Если не совпадает ни один из сохраненных текстов кнопок,
        # извлекаем пример из текста кнопки
        parts = button_text.split(":", 1)
        if len(parts) > 1:
            example_to_use = parts[1].strip()
    
    # Отображаем в консоли информацию для отладки
    print(f"--- SEND_EXAMPLE DEBUG ---")
    print(f"Button text: {button_text}")
    print(f"Example to use: {example_to_use}")
    print(f"Current state: {current_state}")
    print(f"Current step: {current_step}")
    
    if not example_to_use:
        await message.reply(
            "⚠️ Ошибка: не удалось определить пример. Попробуйте снова." if language == "ru" else
            "⚠️ Error: could not determine the example. Please try again." if language == "en" else
            "⚠️ Errore: impossibile determinare l'esempio. Riprova." if language == "it" else
            "⚠️ Fehler: Das Beispiel konnte nicht ermittelt werden. Bitte versuchen Sie es erneut."
        )
        return
    
    # Сообщаем пользователю, какой пример используется
    await message.reply(
        f"✅ Используется пример: {example_to_use}" if language == "ru" else
        f"✅ Using example: {example_to_use}" if language == "en" else
        f"✅ Usando esempio: {example_to_use}" if language == "it" else
        f"✅ Beispiel verwendet: {example_to_use}"
    )
    
    # Сохраняем пример в ответах в зависимости от текущего состояния
    answers = user_data.get("answers", {})
    
    # Определяем ключ для хранения ответа на основе current_state
    answer_key = None
    if current_state == "waiting_for_date":
        answer_key = "date"
    elif current_state == "waiting_for_start_time":
        answer_key = "start_time"
    elif current_state == "waiting_for_end_time":
        answer_key = "end_time"
    elif current_state == "waiting_for_student_name":
        answer_key = "student_name"
    elif current_state == "waiting_for_student_age":
        answer_key = "student_age"
    elif current_state == "waiting_for_lesson_topic":
        answer_key = "lesson_topic"
    elif current_state == "waiting_for_homework":
        answer_key = "homework"
    elif current_state == "waiting_for_feedback":
        answer_key = "feedback"
    elif current_state == "waiting_for_comment":
        answer_key = "comment"
    
    if answer_key:
        answers[answer_key] = example_to_use
        print(f"Saved example {example_to_use} as {answer_key}")
    else:
        print(f"Warning: could not determine answer key for state {current_state}")
    
    # Обновляем данные состояния и переходим к следующему шагу
    await state.update_data(answers=answers, current_step=current_step + 1)
    await ask_next_parameter(message, state)


async def finish_report(message: Message, state: FSMContext) -> None:
    """Завершение создания отчета и его генерация."""
    user_data = await state.get_data()
    language = user_data.get("language", "ru")
    answers = user_data.get("answers", {})
    
    print(f"--- FINISH REPORT DEBUG ---")
    print(f"User data: {user_data}")
    print(f"Language: {language}")
    print(f"Answers: {answers}")
    
    # Сообщение о том, что отчет генерируется
    waiting_message = await message.reply(
        "⏳ Пожалуйста, подождите. Генерируется отчет..." if language == "ru" else
        "⏳ Please wait. Generating report..." if language == "en" else
        "⏳ Attendere prego. Generazione del rapporto in corso..." if language == "it" else
        "⏳ Bitte warten. Bericht wird generiert..."
    )
    
    # Очищаем состояние, но сохраняем язык
    await state.clear()
    await state.update_data(language=language)

    # Подготовка параметров и ответов для генерации отчета
    collected_parameters = []
    collected_answers = []

    param_names = {
        "date": ["Дата урока", "Lesson date", "Data della lezione", "Datum der Stunde"],
        "start_time": ["Время начала урока", "Lesson start time", "Ora di inizio della lezione", "Startzeit der Stunde"],
        "end_time": ["Время окончания урока", "Lesson end time", "Ora di fine della lezione", "Endzeit der Stunde"],
        "student_name": ["Имя ученика", "Student name", "Nome dello studente", "Name des Schülers"],
        "student_age": ["Возраст ученика", "Student age", "Età dello studente", "Alter des Schülers"],
        "lesson_topic": ["Тема урока", "Lesson topic", "Argomento della lezione", "Thema der Stunde"],
        "homework": ["Домашнее задание", "Homework", "Compiti a casa", "Hausaufgaben"],
        "feedback": ["Обратная связь от ученика", "Student feedback", "Feedback dello studente", "Feedback des Schülers"],
        "comment": ["Общий комментарий репетитора", "Tutor's comment", "Commento del tutor", "Kommentar des Tutors"]
    }

    lang_idx = 0 if language == "ru" else 1 if language == "en" else 2 if language == "it" else 3
    
    # Проверка на валидность данных ответов
    for param_key, param_values in param_names.items():
        param_name = param_values[lang_idx]
        if param_key in answers and answers[param_key]:
            # Проверяем, что ответ не содержит текст кнопки "Отправить пример"
            answer_text = answers[param_key]
            if "Отправить пример" not in answer_text and "Send example" not in answer_text:
                collected_parameters.append(param_name)
                collected_answers.append(answer_text)
                print(f"Added parameter: {param_name} = {answer_text}")
            else:
                print(f"Skipping parameter {param_name} because it contains button text")
        else:
            print(f"Parameter {param_name} is missing in answers")
    
    # Если нет достаточного количества параметров, используем примеры по умолчанию
    example_texts = {
        "ru": [
            "15.03.2024",  # Дата
            "18:00",       # Время начала
            "19:00",       # Время окончания
            "Алексей",     # Имя ученика
            "12",          # Возраст
            "Математика: дроби",  # Тема
            "Решить задачи 1-5 на странице 42",  # ДЗ
            "Понравилось, было интересно",  # Отзыв
            "Хорошо усваивает материал"  # Комментарий
        ],
        "en": [
            "15.03.2024",
            "6:00 PM",
            "7:00 PM",
            "Alex",
            "12",
            "Math: fractions",
            "Solve problems 1-5 on page 42",
            "Enjoyed it, was interesting",
            "Understands the material well"
        ],
        "it": [
            "15.03.2024",
            "18:00",
            "19:00",
            "Alessandro",
            "12",
            "Matematica: frazioni",
            "Risolvere i problemi 1-5 a pagina 42",
            "È piaciuto, è stato interessante",
            "Comprende bene il materiale"
        ],
        "de": [
            "15.03.2024",
            "18:00",
            "19:00",
            "Alexander",
            "12",
            "Mathematik: Brüche",
            "Löse Aufgaben 1-5 auf Seite 42",
            "Hat Spaß gemacht, war interessant",
            "Versteht das Material gut"
        ]
    }
    
    # Если мало параметров, заполняем недостающие примерами
    if len(collected_parameters) < 4:  # Минимально 4 параметра для нормального отчета
        examples = example_texts[language]
        
        # Проходим по всем параметрам, которых нет в collected_parameters
        for i, (param_key, param_values) in enumerate(param_names.items()):
            param_name = param_values[lang_idx]
            if param_name not in collected_parameters and i < len(examples):
                collected_parameters.append(param_name)
                collected_answers.append(examples[i])
                print(f"Added example parameter: {param_name} = {examples[i]}")

    print(f"Final collected_parameters: {collected_parameters}")
    print(f"Final collected_answers: {collected_answers}")
    
    try:
        # Начало отсчета времени
        start_time = time.time()
        
        # Генерация отчета с использованием Yandex GPT
        print("Calling report_gen (Yandex GPT)...")
        report = report_gen(collected_parameters, collected_answers, language)
        
        # Конец отсчета времени и вычисление длительности
        end_time = time.time()
        generation_time = round(end_time - start_time, 2)
        
        print(f"Generated report: {report[:100]}...")  # Выводим первые 100 символов отчета
        
        # Создаем клавиатуру с кнопкой "Написать новый отчет"
        kb = [
            [KeyboardButton(text="📝 Написать новый отчет" if language == "ru" else 
                          "📝 Write a new report" if language == "en" else 
                          "📝 Scrivi un nuovo rapporto" if language == "it" else 
                          "📝 Neuen Bericht schreiben")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        
        # Добавляем информацию о времени генерации к отчету
        time_info = (
            f"\n\n⏱️ Отчет сгенерирован за {generation_time} секунд." if language == "ru" else
            f"\n\n⏱️ Report generated in {generation_time} seconds." if language == "en" else
            f"\n\n⏱️ Rapporto generato in {generation_time} secondi." if language == "it" else
            f"\n\n⏱️ Bericht generiert in {generation_time} Sekunden."
        )
        
        # Удаляем сообщение об ожидании
        await waiting_message.delete()
        
        # Отправка отчета пользователю с информацией о времени
        await message.reply(
            "📄 Отчет сформирован:\n\n" + report + time_info if language == "ru" else
            "📄 Report generated:\n\n" + report + time_info if language == "en" else
            "📄 Rapporto generato:\n\n" + report + time_info if language == "it" else
            "📄 Bericht erstellt:\n\n" + report + time_info, reply_markup=keyboard)
    except Exception as e:
        print(f"Error generating report: {e}")
        # Удаляем сообщение об ожидании
        await waiting_message.delete()
        
        await message.reply(
            "⚠️ Произошла ошибка при генерации отчета. Пожалуйста, попробуйте снова." if language == "ru" else
            "⚠️ An error occurred while generating the report. Please try again." if language == "en" else
            "⚠️ Si è verificato un errore durante la generazione del rapporto. Si prega di riprovare." if language == "it" else
            "⚠️ Bei der Erstellung des Berichts ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.")

    # Не показываем главное меню - теперь используем клавиатуру с кнопкой написания нового отчета 