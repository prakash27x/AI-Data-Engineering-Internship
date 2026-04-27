import csv

print("\n 1. Which country out of Nepal, India, USA, UK and Australia published the most headlines today?")
# df = pd.read_csv("news_data.csv")
# country_counts = df['sourceCountry'].value_counts()
# most_common_country = country_counts.idxmax()
# print(f"The country that published the most headlines today is: {most_common_country}")

country_code_name_mapping = {
    "np": "Nepal",
    "in": "India",
    "us": "USA",
    "gb": "UK",
    "au": "Australia"
}

country_counts = {code: 0 for code in country_code_name_mapping}

with open("news_data.csv", "r", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        country_code = row.get("sourceCountry", "").strip().lower()
        if country_code in country_counts:
            country_counts[country_code] += 1

max_country = max(country_counts, key=country_counts.get)
max_count = country_counts[max_country]

if max_count == 0:
    print("No headlines found for the selected countries.")
else:
    print(f" Country: {country_code_name_mapping[max_country]},\n Headlines Published: {max_count}")

# --------------------------------------------------------------------------------------
print("\n 2. What is the average number of words in a headline title — per country?")
# two dictionary to store totals and counts for each country
word_totals = {code: 0 for code in country_code_name_mapping}
headline_counts = {code: 0 for code in country_code_name_mapping}

with open("news_data.csv", "r", encoding="utf-8") as file:
    import csv
    reader = csv.DictReader(file)
    for row in reader:
        country_code = row.get("sourceCountry", "")
        title = row.get("title", "")
        if country_code in word_totals and title:
            word_count = len(title.split())
            word_totals[country_code] += word_count
            headline_counts[country_code] += 1

for code, total_words in word_totals.items():
    count = headline_counts[code]
    avg = total_words / count if count > 0 else 0
    print(f"{country_code_name_mapping[code]}: {avg:.2f} words per headline")

# --------------------------------------------------------------------------------------------------
print("\n 3. Are there any headlines that appeared in more than one country? If yes, which ones?")
headline_countries = {}
with open("news_data.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        title = row.get("title", "")
        country_code = row.get("sourceCountry", "")
        if title and country_code:
            if title not in headline_countries:
                headline_countries[title] = set()
            headline_countries[title].add(country_code)

found = False
for title, countries in headline_countries.items():
    if len(countries) > 1:
        print(f"Headline: {title}\nAppeared in countries: {', '.join(countries)}\n")
        found= True
if not found:
    print("NO headline appeared in more than one countries")

# --------------------------------------------------------------------------------------------
print("\n 4. Which news source published the most headlines across all 5 countries combined?")
country_codes = {"np", "in", "us", "gb", "au"}
source_counts = {}

with open("news_data.csv", "r", ) as file:
    import csv
    reader = csv.DictReader(file)
    for row in reader:
        country_code = row.get("sourceCountry", "")
        source_name = row.get("sourcename", "")  # Adjust key if your column is named differently
        if country_code in country_codes and source_name:
            source_counts[source_name] = source_counts.get(source_name, 0) + 1

if source_counts:
    max_source = max(source_counts, key=source_counts.get)
    print(f"News source with most headlines: {max_source} ({source_counts[max_source]} headlines)")
else:
    print("No sources found for the selected countries.")


# ----------------------------------------------------------------------------------------------------------
print("\n 5. What percentage of all headlines were published in the last 6 hours vs older than 6 hours?")
from datetime import datetime, timedelta, UTC
import csv

recent = 0
older = 0
total = 0

now = datetime.now(UTC)

with open("news_data.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        published_at = row.get("publishedAt", "")
        if published_at and published_at != "N/A":
            try:
                pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                if now - pub_time <= timedelta(hours=6):
                    recent += 1
                else:
                    older += 1
                total += 1
            except Exception:
                continue

if total > 0:
    print(f"Published in last 6 hours: {recent/total*100:.2f}%")
    print(f"Published more than 6 hours ago: {older/total*100:.2f}%")
else:
    print("No valid timestamps found.")

# ----------------------------------------------------------------------------------------------------------  
# 6. If you run your script twice, does your database end up with duplicate rows? How did you prevent that?
print("\n 7. Save only headlines with a title longer than 6 words to a CSV. How many passed that filter?")

count = 0
with open("news_data.csv", "r", encoding="utf-8") as infile, \
     open("headlines_longer_than_6_words.csv", "w", encoding="utf-8", newline="") as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        title = row.get("title", "")
        if len(title.split()) > 6:
            writer.writerow(row)
            count += 1

print(f"Number of headlines with title longer than 6 words: {count}")


# ----------------------------------------------------------------------------------------------
print("\n 8. Which country had the longest headline on average — and which had the shortest?")

word_totals = {code: 0 for code in country_code_name_mapping}
headline_counts = {code: 0 for code in country_code_name_mapping}

with open("news_data.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        country_code = row.get("sourceCountry", "").strip().lower()
        title = row.get("title", "")
        if country_code in word_totals and title:
            word_count = len(title.split())
            word_totals[country_code] += word_count
            headline_counts[country_code] += 1

averages = {}
for code in country_code_name_mapping:
    count = headline_counts[code]
    avg = word_totals[code] / count if count > 0 else 0
    averages[code] = avg

longest = max(averages, key=averages.get)
shortest = min(averages, key=averages.get)

print(f"Country with longest average headline: {country_code_name_mapping[longest]} ({averages[longest]:.2f} words)")
print(f"Country with shortest average headline: {country_code_name_mapping[shortest]} ({averages[shortest]:.2f} words)")