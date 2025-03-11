import requests
from bs4 import BeautifulSoup
import json
import csv
import re
import time

# Custom headers to mimic a regular browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
}

def extract_apollo_json(soup_obj):
    """
    Searches for a script tag containing __APOLLO_STATE__ and extracts the JSON
    using a regular expression.
    """
    # Use the "string" parameter to avoid the deprecation warning.
    script_tag = soup_obj.find("script", string=re.compile("__APOLLO_STATE__"))
    if not script_tag or not script_tag.string:
        return None
    script_text = script_tag.string.strip()
    # Regex to capture the JSON object between "window.__APOLLO_STATE__ =" and an optional semicolon.
    pattern = re.compile(r"window\.__APOLLO_STATE__\s*=\s*(\{.*\});?", re.DOTALL)
    match = pattern.search(script_text)
    if not match:
        return None
    json_str = match.group(1)
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

# CSV file to write the store info
csv_file = "home_depot_stores.csv"
header = ["Type", "#", "City", "State", "Zip"]

with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
    # Step 1: Request the store directory page
    directory_url = "https://www.homedepot.com/l/storeDirectory"
    print(f"Fetching store directory from: {directory_url}")
    try:
        response = requests.get(directory_url, headers=headers, timeout=30)
    except Exception as e:
        print(f"Error fetching {directory_url}: {e}")
        exit(1)
        
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for {directory_url}")
        exit(1)
    
    soup = BeautifulSoup(response.text, "html.parser")
    apollo_data = extract_apollo_json(soup)
    if not apollo_data:
        print("Error: Could not extract __APOLLO_STATE__ JSON from the directory page.")
        exit(1)
    
    # Extract state entries from the JSON
    state_entries = apollo_data.get("ROOT_QUERY", {}) \
                               .get("storeDirectory", {}) \
                               .get("storeDirectory", [])
    print(f"Found {len(state_entries)} state entries in the directory.")
    
    # Iterate over each state entry
    for state in state_entries:
        state_name = state.get("stateName", "Unknown")
        state_link = state.get("stateLink")
        if not state_link:
            print(f"No stateLink for {state_name}. Skipping.")
            continue
        
        # Extract state code (e.g. "AL") from the stateLink URL
        state_code = state_link.rstrip("/").split("/")[-1]
        print(f"\nProcessing state: {state_name} ({state_code}) - URL: {state_link}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt+1} for state URL: {state_link}")
                state_response = requests.get(state_link, headers=headers, timeout=30)
                if state_response.status_code != 200:
                    print(f"Error: Received status code {state_response.status_code} for {state_link}")
                    continue
                break  # Success
            except requests.exceptions.Timeout as te:
                print(f"Timeout on attempt {attempt+1} for {state_link}: {te}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    print("Max retries reached. Skipping this state.")
                    state_response = None
                    break
            except Exception as e:
                print(f"Error on attempt {attempt+1} for {state_link}: {e}")
                state_response = None
                break
        
        if state_response is None or state_response.status_code != 200:
            continue

        # Parse the state page and extract the __APOLLO_STATE__ JSON
        state_soup = BeautifulSoup(state_response.text, "html.parser")
        state_apollo_data = extract_apollo_json(state_soup)
        if not state_apollo_data:
            print(f"Warning: Could not extract __APOLLO_STATE__ JSON from {state_link}")
            continue
        
        # Find the key that starts with "storeDirectoryByState(" and contains the correct state code.
        store_directory_by_state = None
        for key, value in state_apollo_data.get("ROOT_QUERY", {}).items():
            if key.startswith("storeDirectoryByState(") and f"\"state\":\"{state_code}\"" in key:
                store_directory_by_state = value
                break
        
        if not store_directory_by_state:
            print(f"Warning: No storeDirectoryByState data found for state {state_name} on {state_link}")
            continue
        
        stores_info = store_directory_by_state.get("storesInfo", [])
        if not stores_info:
            print(f"No stores info found for state {state_name}.")
            continue
        
        print(f"Found {len(stores_info)} stores in state {state_name}.")
        
        # Process each store's info
        for store in stores_info:
            address = store.get("address", {})
            city_val = address.get("city", "")
            state_val = address.get("state", "")
            zip_val = address.get("postalCode", "")
            store_url = store.get("url", "")
            if not store_url:
                raise ValueError(f"Missing store URL for store data: {store}")
            # Extract store id as the last part of the URL (after the last slash) & ensure id is always 4 digits by padding with leading zeros
            store_id_val = store_url.rstrip("/").split("/")[-1].zfill(4)
            
            writer.writerow(["Store", store_id_val, city_val, state_val, zip_val])
        
        print(f"Finished processing state: {state_name}")

print("\nScraping complete. CSV created:", csv_file)
