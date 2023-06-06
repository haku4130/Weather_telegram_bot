from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import weather_tg_bot_token, open_weather_token
from get_weather import get_weather, get_city_name, get_more_weather

bot = Bot(token=weather_tg_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

location_button = KeyboardButton('Погода в вашем городе', request_location=True)
keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(location_button)


@dp.message_handler(Command(['start', 'help']))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот, и я сообщу тебе погоду в том городе, который ты мне "
                         "напишешь.", reply_markup=keyboard1)


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    city = get_city_name(latitude, longitude, open_weather_token)
    if city:
        await message.answer(get_weather(city, open_weather_token), reply_markup=create_inline_keyboard(city))
    else:
        await message.answer('Город не найден, нам очень жаль \U0001F614')


@dp.message_handler()
async def cmd_start(message: types.Message):
    city = message.text
    weather = get_weather(city, open_weather_token)
    await message.answer(weather, reply_markup=create_inline_keyboard(city))


def create_inline_keyboard(city):
    keyboard = InlineKeyboardMarkup(row_width=1)
    tomorrow_button = InlineKeyboardButton("Погода на завтра", callback_data=f"1_{city}")
    five_days_button = InlineKeyboardButton("Погода на 5 дней", callback_data=f"5_{city}")
    keyboard.add(tomorrow_button, five_days_button)
    return keyboard


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith(('1_', '5_')))
async def handle_inline_buttons(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    days = int(data[0])
    city = data[1]
    weather = get_more_weather(city, open_weather_token, days)
    for day in weather:
        await bot.send_message(callback_query.from_user.id, day)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
