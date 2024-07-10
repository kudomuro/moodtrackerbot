from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
from aiogram.utils.callback_data import CallbackData
import sys
import db
sys.path.insert(0, '/home/moodtracker/Desktop/Folder_2')


class OrderFillFormToday(StatesGroup):
    waiting_for_cmd_date = State()
    waiting_for_daynight = State()
    waiting_for_moods = State()
    waiting_for_energy = State()
    waiting_for_event = State()
    waiting_for_finish = State()

callback_dates = CallbackData("fabdate", "date", "daynight")
callback_moods = CallbackData("fabmood", "mood")
callback_energy = CallbackData("fabenergy", "energy")
callback_events = CallbackData("fabevent", "event")
user_data={}

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

async def cmd_date(message: types.Message, state: FSMContext):
    newdate = datetime.now()
    newdate = newdate.strftime("%d.%m.%Y")
    user_data[message.from_user.id] = [newdate]  
    await state.set_state(OrderFillFormToday.waiting_for_daynight.state)    
    await message.answer("Выбери время суток", reply_markup=get_kb_daynight_fab(newdate))    

async def get_mood_fab(message: types.Message):    
    await message.edit_text(f"Какое у тебя настроение?", reply_markup=get_kb_mood_fab())    

async def callbacks_daynight(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["daynight"]
    if action == "morning":
        user_data[call.from_user.id].append("утро")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "day":
        user_data[call.from_user.id].append("день")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "evening":
        user_data[call.from_user.id].append("вечер")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "night":
        user_data[call.from_user.id].append("ночь")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())   
    await state.set_state(OrderFillFormToday.waiting_for_moods.state)
    await call.answer()

async def callbacks_moods(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["mood"]
    if action == "bad":
        user_data[call.from_user.id].append("плохое")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "soso":
        user_data[call.from_user.id].append("не очень")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "normal":
        user_data[call.from_user.id].append("нормальное")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "good":
        user_data[call.from_user.id].append("хорошее")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "perfect":
        user_data[call.from_user.id].append("отличное")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    await state.set_state(OrderFillFormToday.waiting_for_energy.state)
    await call.answer()

async def callbacks_energy(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["energy"]
    if action == "strain":
        user_data[call.from_user.id].append("переутомлен")
        await call.message.edit_text("Укажи событие")
    elif action == "tiny":
        user_data[call.from_user.id].append("очень мало")
        await call.message.edit_text("Укажи событие")
    elif action == "low":
        user_data[call.from_user.id].append("мало")
        await call.message.edit_text("Укажи событие")
    elif action == "normally":
        user_data[call.from_user.id].append("в норме")
        await call.message.edit_text("Укажи событие")
    elif action == "lot":
        user_data[call.from_user.id].append("много")
        await call.message.edit_text("Укажи событие")
    elif action == "surplus":
        user_data[call.from_user.id].append("переизбыток")
        await call.message.edit_text("Укажи событие")   
    await state.set_state(OrderFillFormToday.waiting_for_event.state)
    await call.answer()

async def event_finish(call: types.CallbackQuery, state: FSMContext):
    user_value = user_data.get(call.from_user.id, 0)
    await call.message.edit_text(f"Итого: {user_value}")
    await state.finish()
    
async def get_event(message: types.Message, state: FSMContext):
    user_value = user_data.get(message.from_user.id, 0)
    user_data[message.from_user.id].append(message.text)
    await message.reply(f"Записал информацию: {user_value}")
    await state.finish()

def register_handlers_today(dp: Dispatcher):
    dp.register_message_handler(cmd_date, commands="today", state="*")
    dp.register_callback_query_handler(callbacks_daynight, callback_dates.filter(daynight=["morning", "day", "evening", "night"]), state=OrderFillFormToday.waiting_for_daynight)
    dp.register_callback_query_handler(callbacks_moods, callback_moods.filter(mood=["bad", "soso", "normal", "good", "perfect"]), state=OrderFillFormToday.waiting_for_moods)
    dp.register_callback_query_handler(callbacks_energy, callback_energy.filter(energy=["strain","tiny", "low", "normally", "lot", "surplus"]), state=OrderFillFormToday.waiting_for_energy)
    # dp.register_callback_query_handler(send_random_value, text="finish")
    # dp.register_callback_query_handler(get_event, text = "event")
    dp.register_callback_query_handler(event_finish, text = "event_finish", state=OrderFillFormToday.waiting_for_finish)
    dp.register_message_handler(get_event, state=OrderFillFormToday.waiting_for_event)

