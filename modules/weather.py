import os
import requests

def get_weather(city_name):
    """Belirtilen şehir için OpenWeather API üzerinden hava durumu bilgisi getirir."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Hava durumu API anahtarı eksik."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",
        "lang": "tr"
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get("cod") == 200:
            main = data["main"]
            weather = data["weather"][0]["description"]
            return (f"{city_name} için hava {weather}, "
                    f"sıcaklık {main['temp']}°C, "
                    f"nem %{main['humidity']}.")
        else:
            return f"Hava durumu alınamadı: {data.get('message')}"
    except Exception as e:
        return f"Hava durumu sorgusu başarısız: {e}"
