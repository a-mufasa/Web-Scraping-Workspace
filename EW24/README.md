## `EW24`
Scraper and Parser for exhibitors of the [2024 Expo West](https://www.expowest.com)

To start the process, you will need the 3 python files (`getVendors.py`, `scrape.py`, `parse.py`) and an empty folder titled `pages` (can be changed later on). The simplest way to get this is to clone this repository locally then cd to the EW24 folder in your terminal to run the files.

Go to the [exhibitor list page](https://s15.a2zinc.net/eventmap/public/eventmap.aspx?EventId=1013) and expand the list of all exhibitors and scroll all the way through it to load the content. Afterwords, open the dev console and search for the `<tbody>` that contains the links to all the exhibitors and copy that HTML element. Create an html file in the same folder as the `.py` files and paste the HTML (ex: `vendors.html`). You will then run the following files in order:

### `getVendors.py`
This code will take the HTML pasted from the site and extract all the vendor booth ids into a `vendors.txt` file. 

How to run: `python3 getVendors.py [HTML file]`

### `scrape.py`
This code will take the list of exhibitor booth ids we just extracted and the base url of the site and scrape each exhibitor's page into an output folder. If you have a specific name for the folder you can input that, otherwise it will default to `pages`. Note that the base url in this case is the URL of the exhibitor's page without the ID (ex: https://expowest24.smallworldlabs.com/?page_id=2424&boothId=)

How to run: `python3 scrape.py [vendor IDs file] [base url] [optional output folder]`

### `parse.py`
This code will go through each of the pages that were just scraped and parse through them using Python's `BeautifulSoup` package and push all of the companies' information into a `data.json` file. When running this, you'll need to provide the base_url of the website which is the host in this case (ex: https://expowest24.smallworldlabs.com)

How to run: `python3 parse.py [base url]`
