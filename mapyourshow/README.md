## `mapyourshow`
Scraper and Parser for exhibitors of mapyourshow sites. Example: [2024 Winter Fancy Food Show](https://wff2024.mapyourshow.com/)

To start the process, you will need the 3 python files (`getVendors.py`, `scrape.py`, `parse.py`) and an empty folder titled `pages` (can be changed later on). The simplest way to get this is to clone this repository locally then cd to the WFF24 folder in your terminal to run the files.

Go to the [exhibitor list page](https://wff2024.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false) and expand the list of all exhibitors and scroll all the way through it to load the content. Afterwords, open the dev console and search for the `<ul>` with class=`"cards exh-basic"` that contains the links to all the exhibitors and copy that HTML element. Create an html file in the same folder as the `.py` files and paste the HTML (ex: `vendors.html`). You will then run the following files in order:

### `getVendors.py`
This code will take the HTML pasted from the site and extract all the vendor ids into a `vendors.txt` file. 

How to run:

```
uv run python mapyourshow/getVendors.py [HTML file]
```

### `scrape.py`
This code will take the list of vendor/exhibitor ids we just extracted and the base url of the site and scrape each exhibitor's page into an output folder. If you have a specific name for the folder you can input that, otherwise it will default to `pages`. Note that the base url in this case is the URL of the exhibitor's page without the ID (ex: https://wff2024.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid=)

How to run:

```
uv run python mapyourshow/scrape.py [vendor IDs file] [base url] [optional output folder]
```

### `parse-YYYY.py`
This code will go through each of the pages that were just scraped and parse through them using Python's `BeautifulSoup` package and push all of the companies' information into a `data.json` file. When running this, you'll need to provide the base_url of the website which is the host in this case (ex: https://wff2024.mapyourshow.com)

How to run:

```
uv run python mapyourshow/parse-YYYY.py [base url]
```