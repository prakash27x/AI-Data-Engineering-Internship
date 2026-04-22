import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# Fetch users from JSONPlaceholder API
url = 'https://jsonplaceholder.typicode.com/users'

try:
    with urlopen(url, timeout=10) as response:
        status_code = response.getcode()

        # Check status code
        if status_code == 200:
            users = json.loads(response.read().decode('utf-8'))

            # Loop through users and print name, email, and city
            print("=" * 70)
            print(f"{'Name':<25} {'Email':<35} {'City':<15}")
            print("=" * 70)

            for user in users:
                name = user.get('name', 'N/A')
                email = user.get('email', 'N/A')
                city = user.get('address', {}).get('city', 'N/A')
                print(f"{name:<25} {email:<35} {city:<15}")

            print("=" * 70)
            print(f"Total users fetched: {len(users)}")
        else:
            print(f"Error: Failed to fetch data. Status code: {status_code}")
except HTTPError as e:
    print(f"Error: Failed to fetch data. Status code: {e.code}")
except URLError as e:
    print(f"Error: Failed to fetch data. Reason: {e.reason}")
