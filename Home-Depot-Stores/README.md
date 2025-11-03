# Home Depot Store Scraper

Scraper and Parser for Home Depot store directories. This tool fetches the Home Depot store directory, extracts store details from each state's page, and writes the information (store ID, city, state, and zip) to a CSV file.

## File Structure

- **`scrape.py`**  
  The main Python script that:
  - Requests the Home Depot store directory page at `https://www.homedepot.com/l/storeDirectory`.
  - Extracts the list of states from the embedded JSON (`window.__APOLLO_STATE__`) on that page.
  - Iterates over each state's URL (using the `stateLink` value) to scrape that state's store page.
  - Extracts store details from each state's JSON data, including:
    - **City** (from `address.city`)
    - **State** (from `address.state`)
    - **Zip Code** (from `address.postalCode`)
    - **Store ID** (extracted as the last segment of the store's URL)
  - Writes the extracted details to a CSV file with a fixed `"Store"` type.

- **`homedepot_stores.csv`**  
  The output CSV file produced by the script. It contains the following columns:
  - **Type** (hard-coded to `"Store"`)
  - **#** (Store ID)
  - **City**
  - **State**
  - **Zip**

## How It Works

1. **Fetching the Store Directory:**  
   The script sends an HTTP GET request to `https://www.homedepot.com/l/storeDirectory` with custom headers to mimic a real browser. It then parses the HTML using BeautifulSoup to find the `<script>` tag containing `window.__APOLLO_STATE__` JSON data. A regular expression is used to extract the JSON reliably from the script tag.

2. **Extracting State Information:**  
   The JSON data includes a `storeDirectory` object that holds an array of state entries. Each entry contains the state's name (`stateName`) and its URL (`stateLink`). The script iterates over these entries to process each state individually.

3. **Scraping State Pages:**  
   For each state, the script:
   - Sends an HTTP GET request to the corresponding `stateLink`.
   - Extracts and parses the `window.__APOLLO_STATE__` JSON data from the state's page.
   - Locates the key that starts with `storeDirectoryByState(` (which contains the current state's code) to access the `storesInfo` list.

4. **Extracting Store Data:**  
   From the `storesInfo` list, for every store the script extracts:
   - **City:** From `address.city`
   - **State:** From `address.state`
   - **Zip Code:** From `address.postalCode`
   - **Store ID:** Extracted as the last segment of the store's URL  
     
   The **Type** field is always set to `"Store"`.

5. **Writing CSV:**  
   The collected data is written row by row to the CSV file (`homedepot_stores.csv`) with columns `["Type", "#", "City", "State", "Zip"]`.

## How to Run

From the workspace root:

```
uv run python Home-Depot-Stores/scrape.py
```

Or from within this directory:

```
cd Home-Depot-Stores
uv run python scrape.py
```

Once the script completes, you will find `homedepot_stores.csv` in the same directory with all the scraped store data.

## Troubleshooting

- **JSON Extraction Issues:**  
  If the script fails to locate or parse the `window.__APOLLO_STATE__` JSON data, verify whether Home Depot has changed its page structure. In such cases, you might need to update the regular expression or extraction logic.

- **Timeouts and HTTP Errors:**  
  The script uses a 30-second timeout and a retry mechanism for requests. If you experience frequent timeouts or HTTP errors, consider increasing the timeout value or checking your network connection.

- **Missing Store Data:**  
  If some store details are missing in the output CSV, double-check that the state's page contains the `storesInfo` object with all required fields. The page layout or JSON structure may have been updated.
  