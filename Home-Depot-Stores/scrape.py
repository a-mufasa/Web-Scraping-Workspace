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
    "Cookie": 'akacd_usbeta=3939815398~rv=94~id=058fef8ba415e345d7a86dc6466bbb9f; _bman=6db75a322c2a2bf8c8d0f578a091b19a; HD_DC=origin; bm_mi=04CEE325618A13A86D97B162BE16B2BC~YAAQGvjNF+KOEyqaAQAAUzD/VB1rdeRY0oX1ZHRmi53LXKK1j2705DC78689Qn90AbgmYfp3TWhKK8QyinOxAiEkRNTmjQ79lP6qK1ucCIQYHWa/qpofmti3JeLkXDnhexrJmQD9th2qKBv3AQ22apapyKqLczm9+0NA3zbRZn0uSuEr97UE44grxgHhtE+iflgT0fTUctO4Bvqv5pIMnPsQSAPLrpyi7uMxyucWIFKuRw96HA8vBztVl56kU5nFYBk/Db/Bsa77eGuvGUvSLci8ERwRNSPlHvWkmHxheldMifoFQgyr1OBLIeSl2MkVvsm8SRLO54vgYs1cBs/UJ1o=~1; THD_NR=1; AMCV_F6421253512D2C100A490D45%40AdobeOrg=MCMID|07022189588929767210427086538080640940; THD_PERSIST=; THD_SESSION=; THD_CACHE_NAV_SESSION=; THD_CACHE_NAV_PERSIST=; pxcts=4419e1b8-ba6a-11f0-b973-5ad8eb4d6ea8; _pxvid=4419daea-ba6a-11f0-b972-44855171c165; THD_LOCALIZER=%7B%22WORKFLOW%22%3A%22LOC_HISTORY_BY_IP%22%2C%22THD_FORCE_LOC%22%3A%221%22%2C%22THD_LOCSTORE%22%3A%228445%2BRogers%20-%20Rogers%2C%20AR%2B%22%2C%22THD_STRFINDERZIP%22%3A%2272758%22%2C%22THD_STORE_HOURS%22%3A%221%3B8%3A00-20%3A00%3B2%3B6%3A00-23%3A00%3B3%3B6%3A00-23%3A00%3B4%3B6%3A00-23%3A00%3B5%3B6%3A00-23%3A00%3B6%3B6%3A00-23%3A00%3B7%3B6%3A00-23%3A00%22%2C%22THD_STORE_HOURS_EXPIRY%22%3A1762366202%2C%22THD_INTERNAL%22%3A%220%22%7D; _px_f394gi7Fvmc43dfg_user_id=NDQxZDBlNjEtYmE2YS0xMWYwLTllZTItYzkwYjE3NWI3OWM1; thda.s=d8aa9967-880d-e1e9-23ab-528da55959fe; thda.u=19f65bfd-11ad-74b1-d929-6f6948f1581c; ak_bmsc=F1154033F32B0B23553C52268CCA4E11~000000000000000000000000000000~YAAQGvjNFzKPEyqaAQAA7jP/VB3gTZhbn2o07kUUBT6gGLyk0IeEeVNPH3f9c8DvfeGEsm3fuiiKwgQzqBHsLDiiZ6B+r7ibCEm8AnwxGyi5hbynqZpRFX0VJ+VGazqOkR+E67Gu+zvVfQmRvhDHvviS7+toTwbm7RayP3OUWLlVfGJvzwmr+PWNqIzmdpBsEvNgkHB7KTarhSD9mw6D70z4pKbVW3LHFIha9FRNHojZqbrabiVvAa3kHg7ILjFYVh1Js85T186pnMCR0KxzoKDuvPk8xfNQIm2pVGzRqHaYnKg9NTd6WaIGCnU5qQlrUCgrX0qt7R8A2mUJ9R8y/X2GY5Qjcce+IPtl9EfnBmPidBRUpSt1rsWlH5iuIYfu8i62k8rW4euAktWc/i5G1DzDdOR9GHTgST1fFMD2LewMeo0lQBZgvAhsUMSazM2/rjQWbwHbZeqmN4Iql5VYRC82b9L5Bd36dQe8GVShakSlQ77lUdZObQ30XJBkiJGszZSK; ajs_anonymous_id=749b1b8c-de78-40cc-8b1a-77c31ff4e4b0; trx=4896336394735008320; QSI_HistorySession=https%3A%2F%2Fwww.homedepot.com%2Fl%2FstoreDirectory~1762362604166; _gid=GA1.2.1229532.1762362604; _gcl_au=1.1.799535356.1762362604; _ga=GA1.1.438720440.1762362603; QuantumMetricUserID=a4780b57beca79f79dec373c1c648323; _ga_9H2R4ZXG4J=GS2.1.s1762362603$o1$g0$t1762362607$j57$l0$h0; _abck=C6BA175076F7D4D88F6BCA3AEB8376EC~0~YAAQGvjNF+WQEyqaAQAAU0j/VA66kj3X746fOd5tHee0U2yAnlwkc/iOQP7TJo3D/xWUg3tUShDjUJn4S5KZneRW5mIg8SiMaPBn9K7hreMM/ab8KXBT821vp2ijfvD0CCPC17y99wChS1Pp4r7Kqk//jrg6n137WzzqLTg/r8OtURy4iQ9bMJSEd15vk8ydmL6Fd0Ec+W8iROBJ8dHZ4VYCoJGheotn6ptItaY8DTwiKRsmxrhaXeUsgTyk7qU16KnXJPO7mbKw6cEcpu0HgBGbJo/5DQi89jB8KNfNk0OydnCp3J1RegFu8MU+MrNoMH9lBMzGB1j37rP+Gv/aPDe3RxDr9acGoAonJofXZwEDQCKCvp9GVPQUz76qQkiXzBaM9/cg2++WkuFmKsOSwcj17kmzaMm0hoyF1gw7kOevKwKXYSxLpWT7A9/DtmFygAmo/PEOPPmW6ilDbwCxBJqmNx5Hi90qkJ2CsQ2n91BWaTCzpj+PKNEMCswl64Cq7qSrUVyaMcX3xkleGQKYc+K0hD4WPY+G5eSymReHp/LXDWlW7jBaQxGVJFaMtPsTzdJ+qO7GzLz9uI9frt+WJw2Pn96AyIsMCj7fSBD0NJslqcqmQezacyNDZfxTiGA=~-1~-1~-1~AAQAAAAE%2f%2f%2f%2f%2fyoHQbmFWM60BQGcVz6%2fmgUfF291E503gmSzEbm%2fTlQGhmLAOgAXgH92fBD5sbOlqMSXoB7IPAeKetVkSKuLKVMnZDghB5EGNrxW~-1; DELIVERY_ZIP=72758; DELIVERY_ZIP_TYPE=AUTO; bm_sz=7DB0065FFBCD137CA37700822FADE498~YAAQDPjNF6YEtjGaAQAADrIuVR1Q/+utE035NmhEni/dfwWS2yGNfqSE736GhiGlWDlizXm+1ArZFSJRwWf+aBbqljA2v/Z2CUFuupYTDDIs6m8MdMQkScq1p2QTe+GX49XwQhefsasqDftL5kapbzKe7VS4WqGK8dy4docWQ1NFYXoMxL+3r93fPTXMr6YIKVM17nEfGjFutePjgw/WjvwpqvJKaWiBnlNu3P4eaqWa3sva5RAiZeaD/pVdSFEY85X36UEHQ3ahwBKQPmdjRGKDPMXyeOEXUPbTLhfW3cmzU5XFHzig7k6dfi/gxcxrpEDs0Ef4Ol2Pg/6mrwt22stUwH+LAXiRCWm38mIioisTFEdSWBZ0tM6SoH1AkcIIebkxGf5jPrLKr4RjdSpbT/CSzgvRc2zjz2VOCZyUnauqxRTlpPZs7VdcUVr3owGEFz8/++IGtr/KWm0=~3688006~4277045; kndctr_F6421253512D2C100A490D45_AdobeOrg_identity=CiYwNzAyMjE4OTU4ODkyOTc2NzIxMDQyNzA4NjUzODA4MDY0MDk0MFISCN7j%5FKelMxABGAEqA09SMjAA8AHc5bqppTM%3D; RT="z=1&dm=www.homedepot.com&si=a0959423-95f7-4667-b617-2564bf07b87c&ss=mhmb0eth&sl=2&tt=qp&obo=1&rl=1"; bm_sv=E067DD2E77FDB920C1488AB7EA778C34~YAAQDPjNF8sEtjGaAQAACLQuVR0y5F28k82ZwHLmlzDMJKsUhLW+y01K8Jiq5nBxKDc6yfvBRl5/2cbelnMnOi8ST9BbuHqpBnCyoOOoHKOE58Qr53oJQEW1v/E2XofjitHOux8/nBejjGMh8DSqbNp5n5OdFiiLQd4b8DahyYKxzaLxxkbSF8ZMiYRbdW0F0HTcItr5S02C34FvNdVMKvHJQPxql8ava20CaYfLYp04TnGDTPALYfA5idI7KxucDJjb~1; forterToken=97ac605e49a34b00892c95d8c07865c0_1762365716844__UDF43-m4_23ck_; bm_ss=ab8e18ef4e; _px=8Q8N6gp38STUA12EBdUpetC03mLIGtvLHuemMuByHqAFjMwTCmhOaepv8R1OMTIaIUl66hXdqlbfIoC6iq0axw==:1000:nwEdbokfBgl3xFxKd6IUMk22QZNRLb+tdipXXq94LYX+1ab+8ICJ2kVAxppuf9FvaQdZ47dR5WnkkZj1btrFAbKXFzXFQ22RRum7NwgVdnPozz5/Qh5o4B0hfGpN63zQU9UhPjfYY7pX24ASAPMqbJFbLbiqHA1EiMvC+wr1D+pnwTwvUm/2xwgw3oeehEoahQhOY+6epqre8rw3tqyUJVlncNQD4f9q/CGCqti1R2ad8zDmXBK7aYKFfj6g674lkjl79pDnOxlFXueot/areg==; _pxde=334ca94283e17e67060eb65af38c03a2e6eba287c5441a2dcf27c190289f3399:eyJ0aW1lc3RhbXAiOjE3NjIzNjk1NzQ3OTB9; QuantumMetricSessionID=c19ff4591efb2923b9de1b0efd7059b4; bm_so=F10F85A2D482E7C38205DB75E096986C180E7FEDB7683C290C21E2F28BAEDA96~YAAQJvjNFw+AHjSaAQAA/plpVQULU1UQP/lhmLhcDHhYtq2vn0f+SEgwe53itDL5XLf7ENCbQMY0w6jx6cj20u8Ax9E7x5TSsipkktPiLXJsnRzFAtgiBkKyNx2m+b57JijQweF8DZEYSD0xi7a0DnZmvcxd0tZgyk6Cf0Y0kPwHQ2Zcpyq4xAWsqF3VV8wRhQF1IRRDbDfDFSYWqsfh4odY74SiYfkIUJl5uef1CR+oYwXVZz8TTpZN+MHcbmTxCNB6c1Y3M1LPxuxxXb4q7IXZlOO2qOXbBqnG+y0TZjq4uYHYfmygrz1GQTdhcBbJc+pJoqHmEcDAv2MCmJfPWss58b9XLoo2m3iWny5wT9/3JwA6e6IU9cc3LGlUStVkwOot06I4enUW0llbN7Ts09+bD6CS6FLRiLyd628CVwJMtaYHCLEfQWcezS21dWdyRFEYr+7i3dRIM9+evOCn8uU=; bm_lso=F10F85A2D482E7C38205DB75E096986C180E7FEDB7683C290C21E2F28BAEDA96~YAAQJvjNFw+AHjSaAQAA/plpVQULU1UQP/lhmLhcDHhYtq2vn0f+SEgwe53itDL5XLf7ENCbQMY0w6jx6cj20u8Ax9E7x5TSsipkktPiLXJsnRzFAtgiBkKyNx2m+b57JijQweF8DZEYSD0xi7a0DnZmvcxd0tZgyk6Cf0Y0kPwHQ2Zcpyq4xAWsqF3VV8wRhQF1IRRDbDfDFSYWqsfh4odY74SiYfkIUJl5uef1CR+oYwXVZz8TTpZN+MHcbmTxCNB6c1Y3M1LPxuxxXb4q7IXZlOO2qOXbBqnG+y0TZjq4uYHYfmygrz1GQTdhcBbJc+pJoqHmEcDAv2MCmJfPWss58b9XLoo2m3iWny5wT9/3JwA6e6IU9cc3LGlUStVkwOot06I4enUW0llbN7Ts09+bD6CS6FLRiLyd628CVwJMtaYHCLEfQWcezS21dWdyRFEYr+7i3dRIM9+evOCn8uU=^1762369576026; bm_s=YAAQJvjNF2CAHjSaAQAAPJ5pVQSsVDQ1Yxy4n6r3R8pSAkFWHq2JaOPyXP87yrPykEqMNqy0TYolPa6i2kmOA6G8AyFw6WNnkahu9G5VQBohNO4vkH49WQQ5zzAv/Ksd4n8nNPUqbWAca+xuxo5X1yvgnJCCPRUJTiMK8CAMgU7LeHjGUb9i+CAu8K/usnb5xH/cvisyCPAy6fYhh4hrulsByfNHRqmb0ZLsK7HF1++8wjZMZOVOl8PZGTY1yj5d822ktkHFnDCkwHtnUGwuIfSt+bG68HNPHJViAWGqI78XmwDo4cnioEigXcVNzTymZ3yGv6Sdihrt67OuPtcN0EoTcJk5Ng8byu+3jszeqb085hktE2CauJ2Uk13JbeHtHOnbwvpj7jVhwM9MHAkgaytEUmVO91MigDF44/8M/Kn+XMIcd1kIrKQKHEZeGgf51N6ePcWC7u0qNh9xXsfJpoYl3rt5TgUqM52BmdWjeVvB0Z1vMUmM3EL+Kkh5zX9IsuPr1NPJvgUG8ug78u7+atSwIfKLxe6RmKwuQr5ie2+g0TVkN4Qor7l3f6AtDJD/lrs00hWlxw=='
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
header = ["Type", "#", "City", "State", "Zip"]

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
    
    # Write existing data first (sorted by state)
    existing_data.sort(key=lambda x: (x[3], x[1]) if len(x) >= 4 else ("", ""))
    for row in existing_data:
        writer.writerow(row)
    
    # Write new stores data (sorted by state and store number)
    new_stores.sort(key=lambda x: (x[3], x[1]))
    for row in new_stores:
        writer.writerow(row)

print(f"\nScraping complete. Total stores written: {len(existing_data) + len(new_stores)}")
print(f"  - Preserved from other states: {len(existing_data)}")
print(f"  - Newly scraped for {target_state if target_state else 'all states'}: {len(new_stores)}")
print(f"CSV updated: {csv_file}")
