import requests
import os
from dotenv import load_dotenv
import csv
import json

load_dotenv()
API_KEY = os.getenv("GNEWS_API_KEY")
BASE_URL = "https://gnews.io/api/v4/search"

response = requests.get(f"{BASE_URL}?q=example&token={API_KEY}")

try:
    if response.status_code == 200:
        data = response.json() # convert json format data into python dictionary 
        # print(json.dumps(data, indent=6))

        file_name = "news_data.csv"
        csv_data_headers = [
           "id", "title", "description", "content", "publishedAt", "sourceCountry", "sourceName", "url"
        ]

        #loading existing url of each news
        existing_ids = set()

        if os.path.exists(file_name):
            with open(file_name, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_ids.add(row["id"])

        # open file in append mode
        with open("news_data.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=csv_data_headers)

            # to check and write header only if the file is new
            if os.stat(file_name).st_size==0:
                writer.writeheader()

            articles = data["articles"]
            for article in articles:
                article_id = article['id']
                        
                # duplicate checking using IDs and writing data into csv file
                if article_id in existing_ids:
                    continue
                
                writer.writerow({
                    'id': article['id'],
                    'title': article.get('title') or "N/A",
                    'description': article.get('description') or "N/A",
                    'content': article.get('content') or "N/A",
                    'publishedAt': article.get('publishedAt') or "N/A",
                    'sourceCountry': article.get('source', {}).get('country') or "N/A",
                    'sourceName': article.get('source', {}).get('name') or "N/A",
                    'url' : article.get('url'),
                })

                # add to set AFTER writing
                existing_ids.add(article_id)
           
    else:
        print(f"Error: Failed to fetch data. Status Code: {response.status_code}")

except Exception as e:
    print(f"Error: Exception occured. Status code: {e.code}")
