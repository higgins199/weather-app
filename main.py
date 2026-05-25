import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Fallback token if environment variable isn't configured
OPENWEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "3bde7c33b8f5d9749b99d39b09a91c7a")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    units = request.args.get('units', 'metric')

    if not city:
        return jsonify({"status": "error", "message": "Missing required query parameter: 'city'"}), 400

    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': units
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"status": "error", "message": data.get("message", "Failed to fetch weather data")}), response.status_code

        # Restructured data mapping main.temp_max and main.temp_min correctly
        processed_weather = {
            "status": "success",
            "location": {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "coordinates": data.get("coord")
            },
            "weather": {
                "condition": data["weather"][0]["main"] if data.get("weather") else "Unknown",
                "description": data["weather"][0]["description"] if data.get("weather") else "Unknown",
                "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png" if data.get("weather") else None
            },
            "metrics": {
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "temp_max": data.get("main", {}).get("temp_max"),  # Fixed missing max temp
                "temp_min": data.get("main", {}).get("temp_min"),  # Fixed missing min temp
                "humidity_percent": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "units": "Celsius" if units == "metric" else "Fahrenheit"
            }
        }

        return jsonify(processed_weather), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"External API connection failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)