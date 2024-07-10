import os
import hashlib
import logging


from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from datetime import datetime
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters.builtin import Text

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

callback_dates = CallbackData("fabdate", "date", "daynight")
callback_moods = CallbackData("fabmood", "mood")
callback_energy = CallbackData("fabenergy", "energy")
callback_events = CallbackData("fabevent", "event")
user_data={}

class Form(StatesGroup):
    event = State()

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
        types.InlineKeyboardButton(text="Указать событие 📝", callback_data="event"),
        types.InlineKeyboardButton(text="Не указывать", callback_data="finish"),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)    
    return keyboard 

@dp.message_handler(commands="today")
async def cmd_numbers(message: types.Message):
    newdate = datetime.now()
    newdate = newdate.strftime("%d.%m.%Y")
    user_data[message.from_user.id] = [newdate]  
    await message.answer("Выбери время суток", reply_markup=get_kb_daynight_fab(newdate))

async def get_mood_fab(message: types.Message):
    await message.edit_text(f"Какое у тебя настроение?", reply_markup=get_kb_mood_fab())
    
@dp.callback_query_handler(callback_dates.filter(daynight=["morning", "day", "evening", "night"]))
async def callbacks_daynight(call: types.CallbackQuery, callback_data: dict):
    user_value = user_data.get(call.from_user.id, 0)
    action = callback_data["daynight"]
    if action == "morning":
        user_data[call.from_user.id].append("06")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "day":
        user_data[call.from_user.id].append("12")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "evening":
        user_data[call.from_user.id].append("20")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())
    elif action == "night":
        user_data[call.from_user.id].append("02")
        await call.message.edit_text("Укажи настроение",reply_markup=get_kb_mood_fab())   
    await call.answer()


@dp.callback_query_handler(callback_moods.filter(mood=["bad", "soso", "normal", "good", "perfect"]))
async def callbacks_moods(call: types.CallbackQuery, callback_data: dict):
    user_value = user_data.get(call.from_user.id, 0)
    action = callback_data["mood"]
    if action == "bad":
        user_data[call.from_user.id].append("bad")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "soso":
        user_data[call.from_user.id].append("soso")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "normal":
        user_data[call.from_user.id].append("normal")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "good":
        user_data[call.from_user.id].append("good")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    elif action == "perfect":
        user_data[call.from_user.id].append("perfect")
        await call.message.edit_text("Укажи количество энергии",reply_markup=get_kb_energy_fab())
    await call.answer()

@dp.callback_query_handler(callback_energy.filter(energy=["strain","tiny", "low", "normally", "lot", "surplus"]))
async def callbacks_energy(call: types.CallbackQuery, callback_data: dict):
    user_value = user_data.get(call.from_user.id, 0)
    action = callback_data["energy"]
    if action == "strain":
        user_data[call.from_user.id].append("strain")
        await call.message.edit_text("Что произошло",reply_markup=get_kb_event())
    elif action == "tiny":
        user_data[call.from_user.id].append("tiny")
        await call.message.edit_text(f"Итого: {user_value}")
    elif action == "low":
        user_data[call.from_user.id].append("low")
        await call.message.edit_text(f"Итого: {user_value}")
    elif action == "normally":
        user_data[call.from_user.id].append("normally")
        await call.message.edit_text(f"Итого: {user_value}")
    elif action == "lot":
        user_data[call.from_user.id].append("lot")
        await call.message.edit_text(f"Итого: {user_value}")
    elif action == "surplus":
        user_data[call.from_user.id].append("surplus")
        await call.message.edit_text(f"Итого: {user_value}")            
    await call.answer()

@dp.callback_query_handler(text="finish")
async def send_random_value(call: types.CallbackQuery):
    user_value = user_data.get(call.from_user.id, 0)
    await call.message.edit_text(f"Итого: {user_value}")

@dp.callback_query_handler(text = "event")
async def get_event(call: types.CallbackQuery):
    await Form.event.set()
    await call.message.reply("Привет! Как тебя зовут?")

# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')

# Сюда приходит ответ с именем
@dp.message_handler(state=Form.event)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event'] = message.text
        user_data[message.from_user.id].append("bad")
    await message.answer(data['event'])
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)