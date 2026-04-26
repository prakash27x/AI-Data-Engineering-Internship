import requests
import csv

# Step 1: Fetch posts from the API
print("Fetching posts from API...")
response = requests.get('https://jsonplaceholder.typicode.com/posts')

if response.status_code == 200:
    posts = response.json()
    print(f"✓ Successfully fetched {len(posts)} posts")

    # Step 2: Save all posts to CSV with columns: id, title, body
    csv_file = 'posts.csv'
    print(f"\nSaving posts to {csv_file}...")

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'body'])
        writer.writeheader()
        for post in posts:
            writer.writerow({
                'id': post['id'],
                'title': post['title'],
                'body': post['body']
            })
    print(f"✓ Saved all posts to {csv_file}")

    # Step 3: Read CSV back and filter posts with title having more than 5 words
    print(f"\nFiltering posts with title > 5 words...")
    filtered_posts = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title_words = len(row['title'].split())
            if title_words > 5:
                filtered_posts.append(row)

    print(f"✓ Found {len(filtered_posts)} posts with titles > 5 words")
    
    # Step 4: Save filtered posts to a new CSV
    filtered_csv_file = 'posts_filtered.csv'
    print(f"\nSaving filtered posts to {filtered_csv_file}...")

    with open(filtered_csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'body'])
        writer.writeheader()
        writer.writerows(filtered_posts)
    print(f"✓ Saved {len(filtered_posts)} filtered posts to {filtered_csv_file}")

    # Display sample of filtered posts
    print("\n" + "=" * 80)
    print("Sample of Filtered Posts (first 3):")
    print("=" * 80)
    for i, post in enumerate(filtered_posts[:3], 1):
        title_words = len(post['title'].split())
        print(f"\nPost #{post['id']} ({title_words} words in title):")
        print(f"Title: {post['title']}")
        print(f"Body: {post['body'][:100]}...")

else:
    print(f"Error: Failed to fetch data. Status code: {response.status_code}")
