import datetime
from time import strptime
import json
import locale

import requests
from django.shortcuts import render

locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')

# Create your views here.
def load_weather_codes(file_path='1.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def index(request):
    current_weather_url_v2 = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&current=temperature_2m,weather_code&timezone=auto"
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search?name={}&count=1&language=ru&format=json"
    forecast_url = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto&forecast_days=6"

    if request.method == "POST":

        city1 = request.POST.get('city1', None)

        weather_data, daily_forecast = fetch_weather_and_forecast(city1, current_weather_url_v2, forecast_url, geocoding_url)


        context = {
            "weather_data": weather_data,
            "daily_forecast": daily_forecast,
        }
        return render(request, "weather_app/index.html", context)
    else:
        return render(request, "weather_app/index.html")


def fetch_weather_and_forecast(city, current_weather_url, forecast_url, geocoding_url):
    weather_codes = load_weather_codes()
    city_coords = requests.get(geocoding_url.format(city)).json()

    lat, lon = round(city_coords['results'][0]['latitude'],2), round(city_coords['results'][0]['longitude'],2)
    response = requests.get(current_weather_url.format(lat, lon)).json()
    forecast_response = requests.get(forecast_url.format(lat, lon)).json()
    current_weather_code_data = weather_codes.get(str(response['current']['weather_code']), {})
    weather_data = {
        "city": city,
        "temperature": round(response['current']['temperature_2m'], 2),
        "description": current_weather_code_data.get('description', 'Неизвестно'),
        "icon": current_weather_code_data.get('image', ''),
    }

    daily_forecast = []

    for i in range(1,len(forecast_response['daily']['time'])):
        date = datetime.datetime.strptime(forecast_response['daily']['time'][i], '%Y-%m-%d')
        f_date = f"{date.strftime('%A').capitalize()}, {date.day} {date.strftime('%B').lower()}"

        code_data = weather_codes.get(str(forecast_response['daily']['weather_code'][i]), {})

        daily_forecast.append({
            "day": f_date,
            "min_temp": forecast_response['daily']['temperature_2m_min'][i],
            "max_temp": forecast_response['daily']['temperature_2m_max'][i],
            "description": code_data.get('description', 'Неизвестно'),
            "icon": code_data.get('image', ''),
        })

    return weather_data, daily_forecast
