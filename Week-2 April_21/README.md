# Week 2 - April 21: API Data Fetching & Analysis

## Overview

This folder contains 3 progressive tasks that cover API data fetching, CSV file handling, and data analysis. All tasks use free public APIs and demonstrate practical skills for working with real-world data sources.

**Date:** April 21, 2026  

---

## 📋 Task List

| # | Task | 
|---|------|
| 1 | Fetch & Print Users | 
| 2 | Fetch & Save to CSV |
| 3 | Real API + Analysis |

---

## Task 1: Fetch & Print Users

### Description
Fetch a list of users from the JSONPlaceholder API and print each user's name, email, and city to the terminal.

### Expected Output
```
Name : Leanne Graham
Email: Sincere@april.biz
City : Gwenborough
-----
Name : Ervin Howell
Email: Shanna@melissa.tv
City : Wisokyburgh
```

### API Used
- **Endpoint:** `https://jsonplaceholder.typicode.com/users`
- **Method:** GET
- **Response:** JSON array of user objects

---

## Task 2: Fetch & Save to CSV

### Description
Fetch posts from the JSONPlaceholder API, save them to CSV format, then filter and save only posts with titles containing more than 5 words.

### Expected Output
```
Fetching posts from API...
Successfully fetched 100 posts

Saving posts to posts.csv...
Saved all posts to posts.csv

Filtering posts with title > 5 words...
Found 65 posts with titles > 5 words

Saving filtered posts to posts_filtered.csv...
Saved 65 filtered posts to posts_filtered.csv
```

### Implementation Details
- Fetches 100 posts from API in single request
- Writes posts to CSV using `csv.DictWriter`
- Reads CSV back using `csv.DictReader`
- Filters posts based on word count in title (splits by whitespace)
- Saves filtered results to new CSV file
- Progress indicators show each step

### API Used
- **Endpoint:** `https://jsonplaceholder.typicode.com/posts`
- **Method:** GET
- **Response:** JSON array of 100 post objects

### CSV Format
**posts.csv:**
```
id,title,body
1,sunt aut facere repellat provident occaecati excepturi optio reprehenderit,"quia et suscipit..."
2,qui est esse,"est rerum tempore vitae..."
```

**posts_filtered.csv:**
```
id,title,body
1,sunt aut facere repellat provident occaecati excepturi optio reprehenderit,"quia et suscipit..."
3,ea molestias quasi exercitationem repellat qui ipsa sit aut,"et iusto sed quo..."
```

---

## Task 3: Real API + Analysis

### Description
Fetch 7-day weather forecast for Kathmandu using the Open-Meteo API (real, production API with no authentication required). Analyze the data to find the hottest and coldest days, and generate a detailed analysis report.

### Files
- `task3_weather_analysis.py` - Main script
- `weather.csv` - 7-day forecast data (auto-generated)
- `weather_summary.txt` - Analysis report (auto-generated)

### Expected Output
```
Fetching weather forecast for Kathmandu...

Saving weather data to weather.csv...
Saved 7 days of weather data

======================================================================
WEATHER ANALYSIS FOR KATHMANDU (7-DAY FORECAST)
======================================================================

HOTTEST DAY: 2026-04-23
   Max Temperature: 31.7°C

COLDEST DAY: 2026-04-27
   Min Temperature: 17.9°C

7-DAY FORECAST SUMMARY:
Date         Max Temp (°C)   Min Temp (°C)  
------------------------------------------
2026-04-22   30.9            19.7           
2026-04-23   31.7            20.3           
2026-04-24   31.3            20.1           
2026-04-25   28.5            21.0           
2026-04-26   28.1            19.4           
2026-04-27   28.2            17.9           
2026-04-28   29.5            19.9           
======================================================================

Saving summary to weather_summary.txt...
Summary saved to weather_summary.txt

Task 3 completed successfully!
```

### Implementation Details
- Fetches data from real-world API (Open-Meteo)
- Uses geographic coordinates: Latitude 27.7172°N, Longitude 85.3240°E
- Requests daily max and min temperatures for 7 days
- Saves forecast to CSV with columns: Date, Max Temperature, Min Temperature
- Analyzes data to find:
  - Hottest day (maximum temperature)
  - Coldest day (minimum temperature)
  - Average temperatures
  - Temperature range
- Generates detailed summary report to text file
- Uses `csv.writer` for CSV export
- Uses `datetime` for timestamp generation

### API Used
- **Endpoint:** `https://api.open-meteo.com/v1/forecast`
- **Method:** GET
- **Location:** Kathmandu, Nepal
- **Latitude:** 27.7172°N
- **Longitude:** 85.3240°E
- **Parameters:**
  - `daily`: temperature_2m_max, temperature_2m_min
  - `timezone`: auto

### CSV Format
**weather.csv:**
```
Date,Max Temperature (°C),Min Temperature (°C)
2026-04-22,30.9,19.7
2026-04-23,31.7,20.3
2026-04-24,31.3,20.1
2026-04-25,28.5,21.0
2026-04-26,28.1,19.4
2026-04-27,28.2,17.9
2026-04-28,29.5,19.9
```

**weather_summary.txt (Sample):**
```
======================================================================
KATHMANDU 7-DAY WEATHER FORECAST ANALYSIS
======================================================================

Generated: 2026-04-22 22:06:22
Location: Kathmandu, Nepal
Latitude: 27.7172°N, Longitude: 85.3240°E

KEY FINDINGS:
----------------------------------------------------------------------
Hottest Day: 2026-04-23
   Maximum Temperature: 31.7°C

Coldest Day: 2026-04-27
   Minimum Temperature: 17.9°C

Average Maximum Temperature: 29.7°C
Average Minimum Temperature: 19.8°C
Temperature Range: 10.0°C
```

---

## 📂 File Structure

```
Week-2 April_21/
├── task_1.py                      # Task 1 - Fetch & Print
├── task_2.py      # Task 2 - Fetch & Save to CSV
├── task_3.py      # Task 3 - Real API + Analysis
├── posts.csv                      # Generated by Task 2
├── posts_filtered.csv             # Generated by Task 2
├── weather.csv                    # Generated by Task 3
├── weather_summary.txt            # Generated by Task 3
└── README.md                      # This file
```

---

## 🛠️ Tools & Technologies Used

| Tool/Technology | Purpose | Usage |
|-----------------|---------|-------|
| Python | Programming language | All tasks |
| `requests` | HTTP library for API calls | Tasks 1, 2, 3 |
| `csv` module | CSV file reading/writing | Tasks 2, 3 |
| `datetime` module | Timestamp generation | Task 3 |
| `json` module | JSON response parsing | Tasks 1, 2 |
| Text Editor | Code writing | All tasks |
| Terminal/CMD | Running scripts | All tasks |

---

## 📦 Requirements

### Python Version
- Python 3.7 or higher

### Required Packages
```
requests>=2.28.0
```

### Installation
```bash
pip install requests
```

### External APIs
- JSONPlaceholder (free, no authentication)
- Open-Meteo (free, no authentication)

---

## 📝 Key Features by Task

### Task 1: task1_fetch_and_print.py
- HTTP GET requests with `requests.get()`
- JSON parsing and data extraction
- Error handling with try-except
- Function definition and reusability
- Formatted string output
- Timeout configuration

### Task 2: task2_fetch_and_filter.py
- API data fetching
- CSV file writing with DictWriter
- CSV file reading with DictReader
- String manipulation (word counting)
- Data filtering logic
- File I/O operations
- Progress indicators

### Task 3: task3_weather_analysis.py
- Real-world API integration
- Geographic coordinate handling
- Temperature data analysis
- Statistical calculations (max, min, average)
- Multiple file format export (CSV + TXT)
- Report generation
- Formatted output with separators

---

## 🔗 Useful Resources

### APIs Used
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/) - Testing & mocking
- [Open-Meteo](https://open-meteo.com/) - Free weather API

### Python Documentation
- [requests Library](https://requests.readthedocs.io/)
- [csv Module](https://docs.python.org/3/library/csv.html)
- [JSON Module](https://docs.python.org/3/library/json.html)
- [datetime Module](https://docs.python.org/3/library/datetime.html)

---

*Last Updated: April 22, 2026*
