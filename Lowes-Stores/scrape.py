import requests
from bs4 import BeautifulSoup
import json
import csv
import re
import urllib.parse
import time

# Custom headers to mimic a regular browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
}

# Load states from the JSON file
with open("states.json", "r", encoding="utf-8") as f:
    states = json.load(f)

# CSV file to write the store info
csv_file = "lowes_stores.csv"
header = ["Type", "#", "City", "State", "Zip"]

with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
    # Loop through each state
    for state in states:
        state_name = state["name"]
        state_id = state["id"]
        encoded_state_name = urllib.parse.quote(state_name.replace(" ", "-"))
        url = f"https://www.lowes.com/Lowes-Stores/{encoded_state_name}/{state_id}"
        print(f"\nScraping URL: {url} (State: {state_name})")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt+1} for URL: {url}")
                response = requests.get(url, headers=headers, timeout=30)
                print(f"Response status code: {response.status_code}")
                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code} for {url}")
                    continue
                break  # Exit retry loop if successful
            except requests.exceptions.Timeout as te:
                print(f"Timeout on attempt {attempt+1} for {url}: {te}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print("Max retries reached. Skipping this URL.")
                    response = None
                    break
            except Exception as e:
                print(f"Error on attempt {attempt+1} for {url}: {e}")
                response = None
                break

        if response is None or response.status_code != 200:
            continue

        try:
            print("Parsing response with BeautifulSoup...")
            soup = BeautifulSoup(response.text, "html.parser")
            
            print("Looking for the <script> tag with __PRELOADED_STATE__...")
            script_tag = soup.find("script", text=re.compile("window.__PRELOADED_STATE__"))
            if not script_tag:
                print(f"Warning: No preloaded state found on {url}")
                continue

            script_content = script_tag.string.strip()
            prefix = "window.__PRELOADED_STATE__ = "
            if script_content.startswith(prefix):
                json_str = script_content[len(prefix):]
            else:
                print(f"Unexpected format in the script tag on {url}")
                continue

            # Remove trailing semicolon if it exists
            if json_str.endswith(";"):
                json_str = json_str[:-1]
                
            print("Loading JSON data...")
            data = json.loads(json_str)
            
            store_directory = data.get("storeDirectory", {})
            if not store_directory:
                print(f"Warning: No storeDirectory found in JSON data from {url}")
                continue
            
            print(f"Found storeDirectory with {len(store_directory)} city keys. Processing each city...")
            # Iterate through each city and its stores in the storeDirectory
            for city_key, stores in store_directory.items():
                print(f"Processing {len(stores)} store(s) for city: {city_key}")
                for store in stores:
                    store_id_val = store.get("id", "")
                    city_val = store.get("city", "")
                    state_val = store.get("state", "")
                    zip_val = store.get("zip", "")
                    
                    writer.writerow(["Store", store_id_val, city_val, state_val, zip_val])
            
            print(f"Finished processing state: {state_name}")
                    
        except Exception as e:
            print(f"Error processing {url}: {e}")

print("\nScraping complete. CSV created:", csv_file)
