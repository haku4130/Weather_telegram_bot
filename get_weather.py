import requests
from pprint import pprint
from datetime import datetime, timedelta
from my_calendar import get_month


def get_wind_side(wind_degree):
    if 0 <= wind_degree < 90:
        return 'СВ'
    if 90 <= wind_degree < 180:
        return 'ЮВ'
    if 180 <= wind_degree < 270:
        return 'ЮЗ'
    if 270 <= wind_degree < 360:
        return 'СЗ'


def get_emoji(weather_type):
    if weather_type == 'Thunderstorm':
        return '\U0001F329'
    if weather_type == 'Rain':
        return '\U0001F327'
    if weather_type == 'Snow':
        return '\U00002744'
    if weather_type in ['Mist', 'Fog']:
        return '\U0001F32B'
    if weather_type == 'Clear':
        return '\U00002600'
    if weather_type == 'Clouds':
        return '\U00002601'


def get_weather(city, token):
    try:
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}&units=metric&lang=ru'
        )
        data = r.json()
        name = data['name']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = int(data['main']['pressure'] * 100 / 133.3)
        wind_speed = data['wind']['speed']
        wind_side = get_wind_side(data['wind']['deg'])
        weather_condition = data['weather'][0]['description'].capitalize()
        weather_emoji = get_emoji(data['weather'][0]['main'])
        result = f'Погода в городе {name} сейчас:\n' \
                 f'{weather_emoji}{weather_condition}\n' \
                 f'\U0001F321Температура: {temp}°C (По ощущениям: {feels_like}°C)\n' \
                 f'\U0001F4A8Ветер {wind_side}, {wind_speed}м/с\n' \
                 f'\U0001F5DCДавление: {pressure} ммрт.ст.\n' \
                 f'\U0001F4A6Влажность воздуха {humidity}%'
        return result
    except Exception as e:
        print(e)
        return 'Неправильное название города'


def get_more_weather(city, token, amount):
    try:
        r = requests.get(
            f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={token}&units=metric&lang=ru'
        )
        data = r.json()
        pprint(data)
        name = data['city']['name']
        all_days = data['list']
        return get_forecast(amount, all_days, name)
    except Exception as e:
        print(e)
        return 'Неправильное название города'


def get_forecast(amount, all_days, city):
    current_date = datetime.now().date()
    res = []
    for i in range(1, amount + 1):
        next_day = current_date + timedelta(days=i)
        forecast_next_day = [item for item in all_days if datetime.fromtimestamp(item["dt"]).date() == next_day]
        weather_descriptions = set(item["weather"][0]["description"] for item in forecast_next_day)
        temp_min = min(item["main"]["temp"] for item in forecast_next_day)
        temp_max = max(item["main"]["temp"] for item in forecast_next_day)
        pop = max(item["pop"] for item in forecast_next_day)
        result = f'Прогноз погоды на {next_day.day} {get_month(next_day.month)} в городе {city}:\n' \
                 f'Общее описание погоды: {", ".join(weather_descriptions)}\n' \
                 f'\U0001F321Макс. температура: {temp_max}°C\n' \
                 f'\U0001F321Мин. температура: {temp_min}°C\n' \
                 f'\U00002614Вероятность осадков: {pop * 100}%'
        res.append(result)
    return res


def get_city_name(lat, lon, token):
    url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={token}"
    response = requests.get(url)
    data = response.json()
    if len(data) > 0:
        city_name = data[0]['name']
        return city_name
    return None
