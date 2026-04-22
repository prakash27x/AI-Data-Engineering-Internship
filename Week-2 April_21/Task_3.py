import requests
import csv
from datetime import datetime

def fetch_weather_forecast():
    """Fetch 7-day weather forecast for Kathmandu using Open-Meteo API"""
    try:
        # Kathmandu coordinates
        latitude = 27.7172
        longitude = 85.3240

        # Open-Meteo API endpoint (free, no key needed)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def save_to_csv(weather_data, filename='weather.csv'):
    """Save weather data to CSV"""
    if not weather_data:
        return

    daily = weather_data.get('daily', {})
    dates = daily.get('time', [])
    max_temps = daily.get('temperature_2m_max', [])
    min_temps = daily.get('temperature_2m_min', [])

    print(f"\nSaving weather data to {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Max Temperature (°C)', 'Min Temperature (°C)'])

        for date, max_temp, min_temp in zip(dates, max_temps, min_temps):
            writer.writerow([date, max_temp, min_temp])

    print(f"Saved {len(dates)} days of weather data")
    return dates, max_temps, min_temps

def analyze_weather(dates, max_temps, min_temps):
    """Analyze weather data to find hottest and coldest days"""
    print("\n" + "=" * 70)
    print("WEATHER ANALYSIS FOR KATHMANDU (7-DAY FORECAST)")
    print("=" * 70)

    # Find max and min temperatures
    max_temp_value = max(max_temps)
    min_temp_value = min(min_temps)

    hottest_day_idx = max_temps.index(max_temp_value)
    coldest_day_idx = min_temps.index(min_temp_value)

    hottest_date = dates[hottest_day_idx]
    coldest_date = dates[coldest_day_idx]

    print(f"\nHOTTEST DAY: {hottest_date}")
    print(f"   Max Temperature: {max_temp_value}°C")

    print(f"\nCOLDEST DAY: {coldest_date}")
    print(f"   Min Temperature: {min_temp_value}°C")

    # Print all days
    print(f"\n7-DAY FORECAST SUMMARY:")
    print(f"{'Date':<12} {'Max Temp (°C)':<15} {'Min Temp (°C)':<15}")
    print("-" * 42)
    for date, max_t, min_t in zip(dates, max_temps, min_temps):
        print(f"{date:<12} {max_t:<15} {min_t:<15}")

    print("=" * 70)

    return {
        'hottest_date': hottest_date,
        'hottest_temp': max_temp_value,
        'coldest_date': coldest_date,
        'coldest_temp': min_temp_value,
        'avg_max': sum(max_temps) / len(max_temps),
        'avg_min': sum(min_temps) / len(min_temps)
    }

def save_summary(analysis, dates, max_temps, min_temps, filename='weather_summary.txt'):
    """Save analysis summary to text file (BONUS)"""
    print(f"\nSaving summary to {filename}...")

    with open(filename, 'w', encoding='utf-8') as file:
        file.write("=" * 70 + "\n")
        file.write("KATHMANDU 7-DAY WEATHER FORECAST ANALYSIS\n")
        file.write("=" * 70 + "\n\n")

        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Location: Kathmandu, Nepal\n")
        file.write(f"Latitude: 27.7172°N, Longitude: 85.3240°E\n\n")

        file.write("KEY FINDINGS:\n")
        file.write("-" * 70 + "\n")
        file.write(f"Hottest Day: {analysis['hottest_date']}\n")
        file.write(f"   Maximum Temperature: {analysis['hottest_temp']}°C\n\n")

        file.write(f"Coldest Day: {analysis['coldest_date']}\n")
        file.write(f"   Minimum Temperature: {analysis['coldest_temp']}°C\n\n")

        file.write(f"Average Maximum Temperature: {analysis['avg_max']:.1f}°C\n")
        file.write(f"Average Minimum Temperature: {analysis['avg_min']:.1f}°C\n")
        file.write(f"Temperature Range: {analysis['avg_max'] - analysis['avg_min']:.1f}°C\n\n")

        file.write("FORECAST DETAILS:\n")
        file.write("-" * 70 + "\n")
        file.write(f"{'Date':<15} {'Max Temp':<15} {'Min Temp':<15}\n")
        file.write("-" * 45 + "\n")

        for date in dates:
            idx = dates.index(date)
            file.write(f"{date:<15} {max_temps[idx]:<15} {min_temps[idx]:<15}\n")

        file.write("\n" + "=" * 70 + "\n")

    print(f"Summary saved to {filename}")

# Main execution
if __name__ == "__main__":
    print("Fetching weather forecast for Kathmandu...")
    weather_data = fetch_weather_forecast()

    if weather_data:
        dates, max_temps, min_temps = save_to_csv(weather_data)
        analysis = analyze_weather(dates, max_temps, min_temps)
        save_summary(analysis, dates, max_temps, min_temps)
        print("\nTask 3 completed successfully!")
    else:
        print("Failed to fetch weather data")
