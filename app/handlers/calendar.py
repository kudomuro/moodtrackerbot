from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
from aiogram.utils.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import re
from typing import List, NamedTuple, Optional
import sys
import db
sys.path.insert(0, '/home/moodtrackerbot')


times = {"1":"утро", "2":"день", "3":"вечер", "4":"ночь"}

class OrderFillFormCalendar(StatesGroup):
    waiting_for_date_c = State()
    waiting_for_daynight_c = State()
    waiting_for_moods_c = State()
    waiting_for_energy_c = State()
    waiting_for_event_c = State()
    waiting_for_finish_c = State()

callback_dates = CallbackData("fabdate", "date", "daynight")
callback_moods = CallbackData("fabmood", "mood")
callback_energy = CallbackData("fabenergy", "energy")
callback_events = CallbackData("fabevent", "event")
user_data={}

start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)

# @dp.message_handler(Text(equals=['Navigation Calendar'], ignore_case=True))
async def nav_cal_handler(message: Message, state: FSMContext):
    await state.set_state(OrderFillFormCalendar.waiting_for_date_c.state)
    await message.answer("Выберите дату: ", reply_markup=await SimpleCalendar().start_calendar())


# simple calendar usage
# @dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        newdate = date.strftime("%d.%m.%Y")
        user_data[callback_query.from_user.id] = [newdate,'','','','']  
        await state.set_state(OrderFillFormCalendar.waiting_for_daynight_c.state)           
        await callback_query.message.answer(
            f'Вы выбрали: {date.strftime("%d/%m/%Y")}\nВыберите время суток',
            reply_markup=get_kb_daynight_fab(newdate)
        )

def get_kb_daynight_fab(mdate):
    buttons = [
        types.InlineKeyboardButton(text="Утро ☕", callback_data=callback_dates.new(date=f"{mdate} 06", daynight="morning")),
        types.InlineKeyboardButton(text="День ☀️", callback_data=callback_dates.new(date=f"{mdate} 12", daynight="day")),
        types.InlineKeyboardButton(text="Вечер 🌆", callback_data=callback_dates.new(date=f"{mdate} 20", daynight="evening")),
        types.InlineKeyboardButton(text="Ночь 🌓", callback_data=callback_dates.new(date=f"{mdate} 02", daynight="night"))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard 

def get_kb_mood_fab():
    buttons = [
        types.InlineKeyboardButton(text="Плохое ⬛", callback_data=callback_moods.new(mood="bad")),
        types.InlineKeyboardButton(text="Не очень 🟪", callback_data=callback_moods.new(mood="soso")),
        types.InlineKeyboardButton(text="Нормальное 🟧", callback_data=callback_moods.new(mood="normal")),
        types.InlineKeyboardButton(text="Хорошое 🟨", callback_data=callback_moods.new(mood="good")),
        types.InlineKeyboardButton(text="Отличное 🟩", callback_data=callback_moods.new(mood="perfect"))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)    
    return keyboard

def get_kb_energy_fab():
    buttons = [
        types.InlineKeyboardButton(text="Переутомлен", callback_data=callback_energy.new(energy="strain")),
        types.InlineKeyboardButton(text="Очень мало", callback_data=callback_energy.new(energy="tiny")),
        types.InlineKeyboardButton(text="Мало", callback_data=callback_energy.new(energy="low")),
        types.InlineKeyboardButton(text="В норме", callback_data=callback_energy.new(energy="normally")),
        types.InlineKeyboardButton(text="Много", callback_data=callback_energy.new(energy="lot")),
        types.InlineKeyboardButton(text="Переизбыток", callback_data=callback_energy.new(energy="surplus"))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)    
    return keyboard 

def get_kb_event():
    buttons = [
        types.InlineKeyboardButton(text="Указать событие 📝", callback_data=callback_events.new(event="event")),
        types.InlineKeyboardButton(text="Не указывать", callback_data=callback_events.new(event="event_finish")),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)    
    return keyboard 

# async def cmd_date(message: types.Message, state: FSMContext):
#     newdate = datetime.now()
#     newdate = newdate.strftime("%d.%m.%Y")
#     user_data[message.from_user.id] = [newdate]  
#     await state.set_state(OrderFillFormToday.waiting_for_daynight_c.state)    
#     await message.answer("Выбери время суток", reply_markup=get_kb_daynight_fab(newdate))    

async def get_mood_fab(message: types.Message):    
    await message.edit_text(f"Какое у тебя настроение?", reply_markup=get_kb_mood_fab())    

async def callbacks_daynight(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["daynight"]
    if action == "morning":
        user_data[call.from_user.id][1]="1"
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "day":
        user_data[call.from_user.id][1]="2"
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "evening":
        user_data[call.from_user.id][1]="3"
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "night":
        user_data[call.from_user.id][1]="4"
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())   
    await state.set_state(OrderFillFormCalendar.waiting_for_moods_c.state)
    await call.answer()

async def callbacks_moods(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["mood"]
    if action == "bad":
        user_data[call.from_user.id][2]="плохое"
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "soso":
        user_data[call.from_user.id][2]="не очень"
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "normal":
        user_data[call.from_user.id][2]="нормальное"
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "good":
        user_data[call.from_user.id][2]="хорошее"
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "perfect":
        user_data[call.from_user.id][2]="отличное"
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    await state.set_state(OrderFillFormCalendar.waiting_for_energy_c.state)
    await call.answer()

async def callbacks_energy(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["energy"]
    if action == "strain":
        user_data[call.from_user.id][3]="переутомлен"
        await call.message.edit_text("Укажи событие")
    elif action == "tiny":
        user_data[call.from_user.id][3]="очень мало"
        await call.message.edit_text("Укажи событие")
    elif action == "low":
        user_data[call.from_user.id][3]="мало"
        await call.message.edit_text("Укажи событие")
    elif action == "normally":
        user_data[call.from_user.id][3]="в норме"
        await call.message.edit_text("Укажи событие")
    elif action == "lot":
        user_data[call.from_user.id][3]="много"
        await call.message.edit_text("Укажи событие")
    elif action == "surplus":
        user_data[call.from_user.id][3]="переизбыток"
        await call.message.edit_text("Укажи событие")   
    await state.set_state(OrderFillFormCalendar.waiting_for_event_c.state)
    await call.answer()

async def event_finish(call: types.CallbackQuery, state: FSMContext):
    user_value = user_data.get(call.from_user.id, 0)
    await call.message.edit_text(f"Итого: {user_value}", add_moods(user_data[call.from_user.id][0],user_data[call.from_user.id][1],user_data[call.from_user.id][2],user_data[call.from_user.id][3],user_data[call.from_user.id][4]))
    await state.finish()
    
async def get_event(message: types.Message, state: FSMContext):
    user_value = user_data.get(message.from_user.id, 0)
    user_data[message.from_user.id][4]=message.text
    try:
        await message.reply(f"Записали информацию: {user_value[0], times[user_value[1]], user_value[2], user_value[3], user_value[4]}", add_moods(user_data[message.from_user.id][0],user_data[message.from_user.id][1],user_data[message.from_user.id][2],user_data[message.from_user.id][3],user_data[message.from_user.id][4]))
    except:
        await message.reply(f"Обновили информацию: {user_value[0], times[user_value[1]], user_value[2], user_value[3], user_value[4]}", update_moods(user_data[message.from_user.id][0],user_data[message.from_user.id][1],user_data[message.from_user.id][2],user_data[message.from_user.id][3],user_data[message.from_user.id][4]))
    await state.finish()

def register_handlers_calendar(dp: Dispatcher):
    dp.register_message_handler(nav_cal_handler, commands="calendar", state="*")
    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(), state=OrderFillFormCalendar.waiting_for_date_c)
    dp.register_callback_query_handler(callbacks_daynight, callback_dates.filter(daynight=["morning", "day", "evening", "night"]), state=OrderFillFormCalendar.waiting_for_daynight_c)
    dp.register_callback_query_handler(callbacks_moods, callback_moods.filter(mood=["bad", "soso", "normal", "good", "perfect"]), state=OrderFillFormCalendar.waiting_for_moods_c)
    dp.register_callback_query_handler(callbacks_energy, callback_energy.filter(energy=["strain","tiny", "low", "normally", "lot", "surplus"]), state=OrderFillFormCalendar.waiting_for_energy_c)
    dp.register_callback_query_handler(event_finish, text = "event_finish", state=OrderFillFormCalendar.waiting_for_finish_c)
    dp.register_message_handler(get_event, state=OrderFillFormCalendar.waiting_for_event_c)


def add_moods(date:str, time:str, mood:str, energy:str,event:str):
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    inserted_row_id = db.insert("moods", {
        "date": date,
        "time": time,
        "mood": mood,
        "energy": energy,
        "event": event
    })
def update_moods(date:str, time:str, mood:str, energy:str,event:str):
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    inserted_row_id = db.update(date, time, mood, energy, event)