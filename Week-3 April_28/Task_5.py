# Task 05 · The Full System [Hard — Capstone]
# Bring everything together — Weeks 1, 2, and 3 in one script
# Build a complete automated data system — fetch, store, analyse, and export. No manual steps.

import csv
import json
import os
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
import mysql.connector

from dotenv import load_dotenv

query_fields = ["name","capital", "languages", "population", "area", "region",  "currencies"]

def fetch_data():
    try:
        load_dotenv()
        base_url = os.getenv("RESTCOUNTRIES_API_URL")

        # Convert list → comma-separated string
        params = {
            "fields": ",".join(query_fields)
        }
        query_string = urlencode(params) #
        url = f"{base_url}?{query_string}"
        response = urlopen(url, timeout=10)
        data = json.loads(response.read())
        # print(json.dumps(data[:2], indent=4)) 
        return data
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def store_data(countries_data):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS countries_db")
        cursor.execute("USE countries_db")
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                capital VARCHAR(255),
                languages TEXT,
                population BIGINT,
                area FLOAT,
                region VARCHAR(255),
                currencies TEXT )
        """)
        insert_query = """
            INSERT IGNORE INTO countries (name, capital, languages, population, area, region, currencies)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for country in countries_data:
            cursor.execute(insert_query, (
                country.get("name", {}).get("common", None),
                (country.get("capital") or [None])[0],
                ", ".join(country.get("languages", {}).values()) or None,
                country.get("population", None),
                country.get("area", None),
                country.get("region", None),
                ", ".join( [c.get("name") for c in country.get("currencies", {}).values()] ) or None
            ))
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error storing data: {err}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():   
            conn.close()

def run_report():
    try:
        conn = mysql.connector.connect(
            host = 'localhost',     
            user = 'root',
            password = 'root',
            database = 'countries_db'
        )
        print("Queried Data From countries_db:")
        print("-" * 60)
        cursor = conn.cursor()
        cursor.execute("SELECT name, population FROM countries ORDER BY population DESC LIMIT 10")
        top_countries = cursor.fetchall()
        print("Top 10 Most Populous Countries:")
        print(f"{'Name':<45} {'Population'}")
        for name, population in top_countries:
            print(f"{name:<45} {population}")

        print("-" * 32)
        cursor.execute("SELECT region, COUNT(*) FROM countries GROUP BY region")
        region_counts = cursor.fetchall()
        print("\nNumber of Countries by Region:")
        print(f"{'Region':<20} {'Count'}")
        for region, count in region_counts:
            print(f"{region:<20} {count}")
        
        print("-" * 60)
        cursor.execute("SELECT name, area FROM countries ORDER BY area DESC LIMIT 10")
        largest_countries = cursor.fetchall()
        print("\nTop 10 Largest Countries by Area:")
        print(f"{'Name':<45} {'Area (sq km)'}")
        for name, area in largest_countries:
            print(f"{name:<45} {area}")
        
        with open("queried_report.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Name", "Value"])

            for name, pop in top_countries:
                writer.writerow(["population", name, pop])

            writer.writerow([])

            for name, area in largest_countries:
                writer.writerow(["area", name, area])
            
            writer.writerow([]) 

            for region, count in region_counts:
                writer.writerow(["region_count", region, count])

    except mysql.connector.Error as err:
        print(f"Error running report: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
        

countries_data = fetch_data()
store_data(countries_data)
run_report()