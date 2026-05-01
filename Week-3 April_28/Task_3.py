import sqlite3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("OPEN_METEO_API_URL")

cities = [
	{"city": "Kathmandu", "latitude": 27.7172, "longitude": 85.3240},
	{"city": "Pokhara", "latitude": 28.2096, "longitude": 83.9856},
	{"city": "Butwal", "latitude": 27.8103, "longitude": 83.4489},
]

all_rows = []

for city in cities:
	for _ in range(2):
		try:
			response = requests.get(
				API_URL,
				params={
					"latitude": city["latitude"],
					"longitude": city["longitude"],
					"daily": "temperature_2m_max,temperature_2m_min",
					"forecast_days": 7,
					"timezone": "auto",
				},
				timeout=30,
			)
			response.raise_for_status()
			data = response.json()["daily"]
			break
		except requests.RequestException:
			data = None
	else:
		print(f"Could not fetch weather for {city['city']}")
		continue

	for index in range(7):
		all_rows.append(
			(
				city["city"],
				data["time"][index],
				data["temperature_2m_max"][index],
				data["temperature_2m_min"][index],
			)
		)

with sqlite3.connect("weather.db") as conn:
	cursor = conn.cursor()
	cursor.execute("DROP TABLE IF EXISTS forecasts")
	cursor.execute(
		"""
		CREATE TABLE forecasts (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			city TEXT,
			date TEXT,
			max_temp REAL,
			min_temp REAL
		)
		"""
	)
	cursor.executemany(
		"INSERT INTO forecasts (city, date, max_temp, min_temp) VALUES (?, ?, ?, ?)",
		all_rows,
	)
	conn.commit()

	print(f"Inserted {len(all_rows)} rows into weather.db")

	print("Query 1: Which city has the highest average max temperature?")   
	cursor.execute("SELECT city, AVG(max_temp) AS avg_max_temp FROM forecasts GROUP BY city ORDER BY avg_max_temp DESC LIMIT 1")
	query1_result = cursor.fetchone()
	print(f"City: {query1_result[0]}")
	print(f"Average Max Temp: {query1_result[1]:.1f}")

	print("\nQuery 2: Find the single hottest day across all 3 cities")
	cursor.execute("SELECT city, date, max_temp FROM forecasts ORDER BY max_temp DESC LIMIT 1") 
	query2_result = cursor.fetchone()
	hottest_city, hottest_date, hottest_temp = query2_result
	print(f"Hottest Day: {hottest_city} on {hottest_date} with max temp of {hottest_temp}°C") 

	print("\nQuery 3: Find days where the temperature difference (max - min) is greater than 10°C")
	cursor.execute("SELECT city, date, max_temp, min_temp FROM forecasts WHERE (max_temp - min_temp) > 10")
	query3_results = cursor.fetchall()
	print("Days with temperature difference greater than 10°C:")
	for city, date, max_temp, min_temp in query3_results:
		diff = max_temp - min_temp
		print(f"{city} on {date}: Max {max_temp}°C, Min {min_temp}°C, Diff {diff:.1f}°C")

# Save a summary report to a summary.txt file using Python file handling
with open("summary.txt", "w") as report:
	report.write("7-DAY WEATHER FORECAST SUMMARY REPORT\n")
	report.write("-" * 60 + "\n\n")

	report.write("QUERY 1: Which city has the highest average max temperature?\n")
	city, avg_max_temp = query1_result
	report.write(f"{city}: Avg Max Temp = {round(avg_max_temp, 1)}°C\n")

	report.write("-" * 60 + "\n\n")
	report.write("QUERY 2: Find the single hottest day across all 3 cities\n")
	report.write(f"Hottest Day: {hottest_city} on {hottest_date}\n")
	report.write(f"Maximum Temperature: {hottest_temp}°C\n")
	
	report.write("-" * 60 + "\n\n")
	report.write("QUERY 3: Days with temperature difference > 10°C\n")
	if query3_results:
		for city, date, max_temp, min_temp in query3_results:
			diff = max_temp - min_temp
			report.write(f"{city} on {date}: Max {max_temp}°C, Min {min_temp}°C, Difference {diff:.1f}°C\n")
	else:
		report.write("No days found with temperature difference greater than 10°C\n")
	

print("\nSummary report saved to summary.txt")