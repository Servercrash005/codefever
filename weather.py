import tkinter as tk
from tkinter import messagebox
import requests

# Replace with your actual API key from WeatherAPI
API_KEY = "7f8619ccfd08422887a150615250107"

def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return None

        weather = {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temp_c": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"]
        }
        return weather
    except:
        return None

def show_weather():
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    weather = get_weather(city)

    if weather:
        result_label.config(
            text=f"📍 {weather['city']}, {weather['region']} ({weather['country']})\n"
                 f"🌡 Temperature: {weather['temp_c']} °C\n"
                 f"🌤 Condition: {weather['condition']}\n"
                 f"💧 Humidity: {weather['humidity']}%\n"
                 f"🌬 Wind: {weather['wind_kph']} km/h"
        )
    else:
        messagebox.showerror("Error", "Could not retrieve weather data. Please check the city name.")

# GUI
app = tk.Tk()
app.title("Weather App")
app.geometry("400x350")
app.config(bg="#e1f5fe")

tk.Label(app, text="Real-Time Weather (Manual City Input)", font=("Helvetica", 14, "bold"), bg="#e1f5fe").pack(pady=10)

tk.Label(app, text="Enter City Name:", font=("Helvetica", 12), bg="#e1f5fe").pack()
city_entry = tk.Entry(app, font=("Helvetica", 12))
city_entry.pack(pady=5)

tk.Button(app, text="Get Weather", command=show_weather, font=("Helvetica", 12), bg="#29b6f6", fg="white").pack(pady=10)

result_label = tk.Label(app, text="", font=("Helvetica", 12), bg="#e1f5fe")
result_label.pack(pady=20)

app.mainloop()
