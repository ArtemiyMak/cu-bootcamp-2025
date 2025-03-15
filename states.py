from aiogram.fsm.state import State, StatesGroup

class ReportInfo(StatesGroup):
    """Состояния для сбора информации о отчете."""
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
    """Состояния для изменения настроек пользователя."""
    waiting_for_language = State() 