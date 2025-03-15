import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

# Поддерживаемые языки
LANGUAGES = {
    "ru": {"flag": "🇷🇺", "name": "Русский"},
    "en": {"flag": "🇬🇧", "name": "English"},
    "it": {"flag": "🇮🇹", "name": "Italiano"},
    "de": {"flag": "🇩🇪", "name": "Deutsch"},
}

# Параметры для сбора информации об отчете
REPORT_PARAMETERS = [
    ("дату урока", "Lesson date", "Data della lezione", "Datum der Stunde", "waiting_for_date"),
    ("время начала урока", "Lesson start time", "Ora di inizio della lezione", "Startzeit der Stunde", "waiting_for_start_time"),
    ("время окончания урока", "Lesson end time", "Ora di fine della lezione", "Endzeit der Stunde", "waiting_for_end_time"),
    ("имя ученика", "Student name", "Nome dello studente", "Name des Schülers", "waiting_for_student_name"),
    ("возраст ученика", "Student age", "Età dello studente", "Alter des Schülers", "waiting_for_student_age"),
    ("тему урока", "Lesson topic", "Argomento della lezione", "Thema der Stunde", "waiting_for_lesson_topic"),
    ("домашнее задание", "Homework", "Compiti a casa", "Hausaufgaben", "waiting_for_homework"),
    ("обратную связь от ученика", "Student feedback", "Feedback dello studente", "Feedback des Schülers", "waiting_for_feedback"),
    ("общий комментарий репетитора", "Tutor's comment", "Commento del tutor", "Kommentar des Tutors", "waiting_for_comment"),
] 