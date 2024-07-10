from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import markdown
from aiogram.dispatcher import FSMContext
import re
from typing import List, NamedTuple, Optional
import sys
import db
sys.path.insert(0, '/home/moodtrackerbot')

times = {"1":"утро", "2":"день", "3":"вечер", "4":"ночь"}

class Moods(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    date: str
    time: str
    mood: str
    energy: str
    event: str

def last() -> List[Moods]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select * "
        "from moods "
        "order by date desc, time")
    rows = cursor.fetchall()
    last_moods = [Moods(date=row[0], time=row[1], mood=row[2], energy=row[3], event=row[4]) for row in rows]
    return last_moods

async def view_all(message: types.Message, state: FSMContext):
    """Отправляет последние несколько записей о расходах"""
    last_moods = last()
    if not last_moods:
        await message.answer("Пока записей нет")
        return

    last_moods_rows = [
        f"{moods.date}, {moods.time}, настроение: {moods.mood}, количество энергии: {moods.energy}, событие: {moods.event}"
        for moods in last_moods]
    answer_message = "Твои записи:\n\n* " + "\n\n* "\
            .join(last_moods_rows)
    await message.answer(answer_message)
    await state.finish() 

def register_handlers_view(dp: Dispatcher):
    dp.register_message_handler(view_all, commands="view", state="*")