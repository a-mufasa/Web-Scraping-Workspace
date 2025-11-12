import httpx
from bs4 import BeautifulSoup
import json
import csv
import re
import time
import sys
from pathlib import Path

# Custom headers to exactly match browser request
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Cookie": 'akacd_usbeta=3939726350~rv=24~id=f5146134efb5d267d41fd34b8c54f88f; bm_ss=ab8e18ef4e; _bman=b097f90243e40391bb77812e57cd94f1; bm_so=4CC36C6F5622C1EEF12408661951CED715A5BC588CD6D08C5980AFDD2D8F9A9C~YAAQxA7GF10sTDGaAQAAb2WwTwXrsgqfgGMvRupWGF88PHAccptMmRjVkNMbtVhr9FREuE9bG2ZlTtdwc6R/WgtfCsQDEXINxJ7HGXD02GHxjh4BqaxVJ4RqvvKsyNkqdKHTr+hFexjRv2ICV9G8Kfy3d9PXT7PNorfMhZR21NXyyDNil6f2CbMw05uYFodLeIO0xGCJjXlo+Kgwhg5DLEthlvnUZgQ0bfoAduk3Wd6w93NXV+PmrVhQ7TIuqOGWacbojK1y+2jvWNk/3iuJU7f2y2MetjBZIYSrRE20LjTQzz+gM66FSpGeJ0cRjZ6h4sH4Ic8W9JEZ31pIOln0sk2LMBgUF3l4IF3rOBcHuBUkwXjQo+EBuLTlz4uGDmiMinHNQEDUlxndHqpq/eb1scbz5+5yS9rhP1ng+VJf04gMLYWmkJbvtBFzOsusvagg+CldADsuHulU6s8wKFKvGGI=; HD_DC=origin; bm_lso=4CC36C6F5622C1EEF12408661951CED715A5BC588CD6D08C5980AFDD2D8F9A9C~YAAQxA7GF10sTDGaAQAAb2WwTwXrsgqfgGMvRupWGF88PHAccptMmRjVkNMbtVhr9FREuE9bG2ZlTtdwc6R/WgtfCsQDEXINxJ7HGXD02GHxjh4BqaxVJ4RqvvKsyNkqdKHTr+hFexjRv2ICV9G8Kfy3d9PXT7PNorfMhZR21NXyyDNil6f2CbMw05uYFodLeIO0xGCJjXlo+Kgwhg5DLEthlvnUZgQ0bfoAduk3Wd6w93NXV+PmrVhQ7TIuqOGWacbojK1y+2jvWNk/3iuJU7f2y2MetjBZIYSrRE20LjTQzz+gM66FSpGeJ0cRjZ6h4sH4Ic8W9JEZ31pIOln0sk2LMBgUF3l4IF3rOBcHuBUkwXjQo+EBuLTlz4uGDmiMinHNQEDUlxndHqpq/eb1scbz5+5yS9rhP1ng+VJf04gMLYWmkJbvtBFzOsusvagg+CldADsuHulU6s8wKFKvGGI=^1762273551821; AKA_A2=A; bm_mi=EAD958149FF640704E82DFAAB96B2CAE~YAAQxA7GFw0tTDGaAQAAVWqwTx00hOi9WqkurpspE6sI6WFOcodsuGUFNdKxkc+y/ray+trEYM1bAKJsUKdUePSyBYoB+SmITZ4gtedNBwc01O5n63Z/oYgj+Ze0e5cZ6TopDrnUSv118bxgQU5GDEkMouH8NoeUmbkG5Y+tV4g/TbzIvw9yuCJC4wJfQpRWvqaILafqg2Z2B/KOxLJz7/ZISIQ7w2JxLNj7M9ZNRvMVBSZ9lTboD8SVIIJL7FyMSS0PhvJNyVh1lDegZv8uH6jU+7K3g6ZcRPCt/Ta1iUk6P0Am+SJ5MCbb2J1IY8U5LqxMMrTu17dp1sPHXBBfL/M=~1; bm_s=YAAQxA7GFw4tTDGaAQAAVWqwTwQhgY/FwT9idVToq1PYTFGUclpdBECBYE5Dms42bxhif/HtInw19iAlTUSKXa62MpfP1AoqcF4rJmxuMjALaDAiA3OALQ0lfBkzaP9MCoTLmZRggTDd+Zfgw9nf/C1w7s7keCiy0ASHXRYgwIh+ic3AS8Xzfc4y5LR+AhkYkmmy5+1ili57Ln/GKs7dfT4Bymd4ldgv3YLWCtESARbVbbyn95KoeIGISdtOV9XxgBWpG8LMF8DJblU/LoVrEWw8UzWVSBOrUOKW9tMO5gDmp6wWBkGoSxENa1flsotSOKJy2dWicUljgyiCZ+oIWeqeZu56mpqNRl1lxgwgPR9tGiyXODhO7vE58V0+oZuqTvBwalZQ0FrnS1zDyT+UlxBEyVn+VIAGlBDy6RQgBME2YTC3B9i6SagXzwkK/TOxSikn3TdXFK68MkbUhU0BCZnKnAQqW1GJQyeFCwbxemJ05NuWF9i2DhaUzbaysCe3kb3ZgHdyCcqtJ0w7ROrIg6wVjzPOYds9PGfymtilCvAcxh1juzpVAwq0LpNctYDKJz62tDFCjg==; bm_sc=4~1~55136291~YAAQxA7GFw8tTDGaAQAAVWqwTwUMhpTl6P46surv8f9QMkGbkXc+pWBR3oJoLSjUxooz81jtXQip+oEmc5pt7bElKHH2WX9rLHFJahtBtvB+EMjJnBVjhjLUMQu5Ouk1MqUolxL7y4/zj/H3uSazzKF5iaoHSeZuei0h1C4ZQcksB2KtQw91VqrUbW41VrFhoGkmw4cred68Z/Kg0kI8gW+vOpZrJMoO3UZt9WFsXsTnyKgt/Nq/Iq+tBoUH6bwEFuLR24f1WAs5bMpqIVE4LRYSI4dpsqhft3pjZ2W3MJrj0dbts+4yzQ7sPMhND0P1wmbzTkKayccQwRnn7zAxByop4FLQa66A/ZlBAjtADtTlAGA+3h+a2RsuKBRC7b07iZXYPpUJEgZX9AbIaFVxbbH4NlCvaox5W1S5JIuwM0Ls6RUv3AAWSuiA; bm_sz=A52B6926064CE2F5EA7BA1191A9D899A~YAAQxA7GFxAtTDGaAQAAVWqwTx0HEUM0mBrQZpRNcGIfAJwT7dlnRcsBHCJaXhFBRHW6us3nb8D90KA//r+cP5O5K3myXZpB7tnbh6svoSbSZouY7OFN8oYRCq1eYTggdWEj8oxqMRF0Eb9F074nkQBMfQvcb5I4wp8k6DE8CzAZLbws45QCIofqNxhWugrZX+HbV6Tawo1hPfcoQZwOTFDODf3txGDN+8l1ZpTTgGgh47vqoK1MAsN+R2N2x7FtHRtbkLeHobMgW7o4sBFnpLMym/6VYDQCD9w42FcxzyiF8uPsOb57agbFD/UGu7qEoqHxRq2fUvrMJqFyvqrNSuLZJYUkoKx6F0boJVpf93RZ7DAuhaVurZ1mZkAMLHd9GCipWDnyjJkpxwRzFOdQSO8Tmq2A~3486768~4408885; THD_NR=1; IN_STORE_API_SESSION=TRUE; THD_PERSIST=; THD_SESSION=; THD_CACHE_NAV_SESSION=; THD_CACHE_NAV_PERSIST=; THD_LOCALIZER=%7B%22WORKFLOW%22%3A%22LOC_HISTORY_BY_IP%22%2C%22THD_FORCE_LOC%22%3A%221%22%2C%22THD_LOCSTORE%22%3A%228445%2BRogers%20-%20Rogers%2C%20AR%2B%22%2C%22THD_STRFINDERZIP%22%3A%2272758%22%2C%22THD_STORE_HOURS%22%3A%221%3B8%3A00-20%3A00%3B2%3B6%3A00-23%3A00%3B3%3B6%3A00-23%3A00%3B4%3B6%3A00-23%3A00%3B5%3B6%3A00-23%3A00%3B6%3B6%3A00-23%3A00%3B7%3B6%3A00-23%3A00%22%2C%22THD_STORE_HOURS_EXPIRY%22%3A1762277153%2C%22THD_INTERNAL%22%3A%220%22%7D; kndctr_F6421253512D2C100A490D45_AdobeOrg_cluster=or2; AMCV_F6421253512D2C100A490D45%40AdobeOrg=MCMID|71643064233816395673018707157701375570; thda.s=a29fe69e-c4d9-31d3-2f5d-19432407ac4b; thda.u=c7da320a-b4d8-0be7-1faa-817432c10aff; _px_f394gi7Fvmc43dfg_user_id=ZWVlZGY2NDEtYjk5YS0xMWYwLWEyOTctZDM3MzFmNDkyM2Iy; pxcts=eef8b95c-b99a-11f0-aaf9-0a53dbb58eb2; _pxvid=eef8b1d2-b99a-11f0-aaf9-9774e954c8d9; RT="z=1&dm=www.homedepot.com&si=f9630753-2571-4cbb-a298-cdaaaca54821&ss=mhks67wu&sl=1&tt=f0&rl=1&ld=hy"; kndctr_F6421253512D2C100A490D45_AdobeOrg_identity=CiY3MTY0MzA2NDIzMzgxNjM5NTY3MzAxODcwNzE1NzcwMTM3NTU3MFISCJrXwf2kMxABGAEqA09SMjAA8AG%5F2cH9pDM%3D; ak_bmsc=D5B7C52FB52687EF06BC0CA5FB82E63C~000000000000000000000000000000~YAAQxA7GF24tTDGaAQAAW22wTx0ZQF5viyzTyJb+Sg6ARkOwYOlm6/tVxMb9f8U9qHlFRpfPxtCN8dGq5YV32wnYL1LED6GT6x8OyNles88W1v0VR8wysl62e+FDFy6fCCBJ/XvPMXnPcCSBPS9lMApQLh4klU73ZqSisI5X/PA+JNI3xD4yaKSJzpig4xPt9miFbo+3Gsxxhwjww+N7px+6jEV0GRgcF0eTX3XQPWJMsX34DdF4Qv1Njde2U8ybt9aW+2DBiIRUOg65lZjrHs9/uPcOuOYqATleYXkxZk8Ydd8wrHQzJdyVSkIjB7d6LTSSL37Ty8q85PcUS/H2mmVD1gcChK8+xiX+E2Hux8vb9c4AE1siVpxeGletOxLvQMfT+yDvPU1JjMRJVDyd5AWss2TVj+svPo+GpensNu7MV7kZJ+uOPfvlI2aHnKyFFvHgQbGNmzMPzjMU1sX+V9Rio4V2ofB7EhNYBd5DHr9kXqtjFT+S05ZyJQY4fDN3orWu; _abck=A68552DE6A8AE74B59F449599AB696EC~-1~YAAQxA7GF9EtTDGaAQAA0XCwTw7bpbF1txI028XC8+cf6r+jMMrlNGWcOSzntijL8IEjQ/v6jd3kIffwtLazKOD4ylKh//rRSeeZXAphJcFJu0k+v63UaRusgxA+m9kf1fA0Wval1xOYIlY9Pej4oLlGMQP6Hk6bWFzpJ1fVFy3fShAJP29JuTr1MogMYsSmOyKUmQD40DSt3Crpu9MwlKCJtXwgKp9pHLhWr0+nS95JDbONBHblL+scaTWO127Pc0o3VRw8wiHLOXLzV/pug0NTytTjn5BM/HCMQakiNhl+2/TBTtv+mBdI4AAwESCpsWIUaYWSHf7Ko3fHE1B/AeDnZhXHMC7UeSJPzA+fqpqUoXh8YR5S6CGr/kYOCBU3qJerrRCjcj9JXhUq63XwSwXE49NOL9cGMzrdp3LywXLEdswvGHcfrFmho11gEEnnWFrWvA3dgP1U7+l2Br2OgBYBAvCvKaoIFCO9i0gNeeAAHN+e6reVPwKJjuO4gISv7BYctZUi4pgM/0t8T/hwZpyfjqq+haRUQ2Ko8yh8BpBehGAZMDeCy5TBKM6RJOmLtslh1sWbJvMjyQ5fzzEn8JtCHhEekNrPXJmKXRg7lNA=~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2f7h8pEW4Mg7lCEVx2nUJafr1mz4P9zsLscJ26yYzcGnxLlaWUw6YUoAYXyLdKj4PbdtpL1ZOlro1158XKxl2o5twXrOmZbM8FKHC~-1; _px=NpYiL9Yvo6J8m5d/2iKjiRjIllw8si16su/IJ1pu1SIgLml3s5P/IwqpKeJH//GUQhhH5zyZvGSoN1BHXw1lug==:1000:ev4/zJMG3mtMPccqJ0M9gQWUgEwfR+06bYnd92+CpwG6ZzdvZk/RzQwyXQpyIZXfnLR98BCzyj8hCgGw85gtxqMJsgitiD0T3dXHC6HsBkdeu9dYfqHJElVE0Sf9FlC5oh37QUGjHnEmrqcx4n1TEMSpvaYn0KqU0IT21ASl9CvFw5FgdsyTpxGaisJn1iYkz6Y986yj01Eq1dfNhjeC+WzIURfuS46w+eZzh9RPAoPVCxXYRSsj7mkVd1FRXCCCLvOykNw5EIiy6eubTonPRA==; _pxde=357303322e2ba1bfbc1c18696a51c2dadaaa60ae047e7ad655d3e44d2b537d65:eyJ0aW1lc3RhbXAiOjE3NjIyNzM1NTUwMzUsImluY19pZCI6WyJkM2I0MWNiNmNhMzUxN2ZkNTAzZWMwNGMzOTc2YWQ4MSJdfQ=='
}

# Create an HTTP/2 client
client = httpx.Client(http2=True, headers=headers, timeout=30, follow_redirects=True)

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
header = ["location_type", "number", "city", "state", "zip_code"]

# Check if a state code was provided as command-line argument
target_state = None
if len(sys.argv) > 1:
    target_state = sys.argv[1].upper()
    print(f"Target state specified: {target_state}")
    print(f"Will update only {target_state} stores in existing CSV")
else:
    print("No state specified - will scrape all states")

# Read existing CSV data if it exists and we're doing a targeted update
existing_data = []
if target_state and Path(csv_file).exists():
    print(f"Reading existing CSV file: {csv_file}")
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_row = next(reader)  # Read and verify header
        for row in reader:
            # Keep all rows that don't match the target state
            if len(row) >= 4 and row[3] != target_state:
                existing_data.append(row)
    print(f"Preserved {len(existing_data)} stores from other states")

# Collect new stores data
new_stores = []

# Step 1: Request the store directory page
directory_url = "https://www.homedepot.com/l/storeDirectory"
print(f"Fetching store directory from: {directory_url}")
try:
    response = client.get(directory_url)
except Exception as e:
    print(f"Error fetching {directory_url}: {e}")
    client.close()
    exit(1)

if response.status_code != 200:
    print(f"Error: Received status code {response.status_code} for {directory_url}")
    client.close()
    exit(1)

soup = BeautifulSoup(response.text, "html.parser")
apollo_data = extract_apollo_json(soup)
if not apollo_data:
    print("Error: Could not extract __APOLLO_STATE__ JSON from the directory page.")
    print(f"HTML preview (first 1000 chars):\n{response.text[:1000]}")
    client.close()
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
    
    # If target_state is specified, only process that state
    if target_state and state_code.upper() != target_state:
        continue
    
    print(f"\nProcessing state: {state_name} ({state_code}) - URL: {state_link}")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1} for state URL: {state_link}")
            state_response = client.get(state_link)
            if state_response.status_code != 200:
                print(f"Error: Received status code {state_response.status_code} for {state_link}")
                continue
            break  # Success
        except httpx.TimeoutException as te:
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
        
        new_stores.append(["Store", store_id_val, city_val, state_val, zip_val])
    
    print(f"Finished processing state: {state_name}")

# Close the HTTP client
client.close()

# Write the combined data to CSV
print(f"\nWriting combined data to {csv_file}")
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    
    # Step 1: Request the store directory page
    directory_url = "https://www.homedepot.com/l/storeDirectory"
    print(f"Fetching store directory from: {directory_url}")
    try:
        response = client.get(directory_url)
    except Exception as e:
        print(f"Error fetching {directory_url}: {e}")
        client.close()
        exit(1)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for {directory_url}")
        client.close()
        exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    apollo_data = extract_apollo_json(soup)
    if not apollo_data:
        print("Error: Could not extract __APOLLO_STATE__ JSON from the directory page.")
        print(f"HTML preview (first 1000 chars):\n{response.text[:1000]}")
        client.close()
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
                state_response = client.get(state_link)
                if state_response.status_code != 200:
                    print(f"Error: Received status code {state_response.status_code} for {state_link}")
                    continue
                break  # Success
            except httpx.TimeoutException as te:
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

# Close the HTTP client
client.close()

print("\nScraping complete. CSV created:", csv_file)
