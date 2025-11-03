# Lowes Store Scraper

Scraper and Parser for Lowes store directories. This tool goes through all the states listed in a `states.json` file, scrapes each state's Lowes store page, and extracts store details (store ID, city, state, and zip) into a CSV file.

## File Structure

- **`states.json`**  
  A JSON file containing a list of state objects. Each object must have an `"id"` and a `"name"`. This can be manually copied from the client.js file on the `https://www.lowes.com/Lowes-Stores` site. For example:
  ```json
  [
      {
          "id": "AL",
          "name": "Alabama"
      },
      {
          "id": "AK",
          "name": "Alaska"
      },
      ...
  ]
  ```
- **`scrape.py`**  
  The main Python script that:
  - Loads the `states.json` file.
  - Constructs URLs for each state (converting spaces in state names to dashes).
  - Scrapes the Lowes store directory pages.
  - Extracts store information from the page's JSON data.
  - Writes the extracted store details to a CSV file.
- **`lowes_stores.csv`**  
  The output CSV file created by the script. It contains the following columns:
  - **Type** (hard-coded to `"Store"`)
  - **#** (Store ID)
  - **City**
  - **State**
  - **Zip**

## How It Works

1. **Loading States:**  
   The script reads the state data from `states.json`.

2. **URL Construction:**  
   For each state, the URL is constructed using the following pattern:
   ```
   https://www.lowes.com/Lowes-Stores/{State-Name-With-Dashes}/{State-ID}
   ```
   *Example:*  
   For `"Alabama"`, the URL becomes `https://www.lowes.com/Lowes-Stores/Alabama/AL`.

3. **Scraping and Parsing:**  
   - The script sends an HTTP GET request to the constructed URL.
   - It uses a custom User-Agent header to mimic a typical browser.
   - If the request times out (after a 30-second timeout) or fails, the script retries a few times.
   - Once the HTML is retrieved, BeautifulSoup is used to parse the page.
   - The script looks for a `<script>` tag containing the `window.__PRELOADED_STATE__` JSON data.
   - It extracts the JSON string (removing the JavaScript assignment prefix and any trailing semicolon) and loads it into a Python dictionary.

4. **Extracting Data:**  
   - From the JSON data, the script extracts the `storeDirectory` object.
   - `storeDirectory` is a dictionary where each key is a city name, and the corresponding value is an array of store objects.
   - For each store, the following fields are extracted:
     - **Store ID** (`id`)
     - **City** (`city`)
     - **State** (`state`)
     - **Zip** (`zip`)

5. **Writing CSV:**  
   - The script writes each store’s data as a row in `lowes_stores.csv`.
   - The **Type** column is always set to `"Store"`.

## How to Run

Ensure that the `states.json` file is correctly formatted and located in the `Lowes-Stores` directory.

From the workspace root:

```
uv run python Lowes-Stores/scrape.py
```

Or from within this directory:

```
cd Lowes-Stores
uv run python scrape.py
```

Once the script finishes, you will find `lowes_stores.csv` in the directory with all the scraped store data.

## Troubleshooting

- **Timeouts and Slow Responses:**  
  The script uses a 30-second timeout with a retry mechanism. If you continue to experience timeouts, consider increasing the timeout value or checking your internet connection.

- **URL Construction Issues:**  
  The script replaces spaces in state names with dashes to match Lowes' URL pattern. Ensure that the names in your `states.json` file are correct.

- **Missing Data:**  
  If the expected `<script>` tag or JSON data isn't found, check if the page structure has changed. You might need to update the script accordingly.
