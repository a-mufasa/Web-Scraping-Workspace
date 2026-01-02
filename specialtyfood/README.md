## `specialtyfood`
Scraper and Parser for exhibitors of Specialty Food Association events. Example: [Winter FancyFaire](https://events.specialtyfood.com/event/winter-fancyfaire/exhibitors/)

To start the process, you will need the 2 python files (`scrape.py`, `parse.py`) and an empty folder titled `pages` (can be changed later on). The simplest way to get this is to clone this repository locally then cd to the specialtyfood folder in your terminal to run the files.

Go to the [exhibitors page](https://events.specialtyfood.com/event/winter-fancyfaire/exhibitors/RXZlbnRWaWV3XzEyMTQzMDM=) and scroll all the way through it to load all the exhibitor content. Afterwords, open the dev console and search for the element that contains all the exhibitor links (the `<a>` tags with hrefs like `/event/winter-fancyfaire/exhibitor/...`) and copy that HTML. Create an html file in the same folder as the `.py` files and paste the HTML (ex: `vendors.html`). You will then run the following files in order:

### `scrape.py`
This code will take the HTML pasted from the site and extract all the exhibitor URLs, then scrape each exhibitor's page into an output folder. If you have a specific name for the folder you can input that, otherwise it will default to `pages`. Note that the base url in this case is the host of the website (ex: https://events.specialtyfood.com)

How to run:

```
uv run python specialtyfood/scrape.py [vendors HTML file] [base url] [optional output folder]
```

Example:
```
uv run python specialtyfood/scrape.py vendors.html https://events.specialtyfood.com pages
```

### `parse.py`
This code will go through each of the pages that were just scraped and parse through them using Python's `BeautifulSoup` package and push all of the companies' information into a `specialtyfood_exhibitors.csv` file.

How to run:

```
uv run python specialtyfood/parse.py
```RXZlbnRWaWV3XzEyMTQzMDM=
