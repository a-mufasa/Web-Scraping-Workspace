# Web Scraping Workspace

Repository for one-off web scraping/parsing projects. Note that some of these websites are **private**, therefore you will not be able to run the scraping/parsing. As such, any private data will be ommitted from this repository.

## `PLMA`
HTML Parser made in JavaScript specifically for [Private Label Manufacturers Association Trade Show](https://members.plma.com/trade-show-directory)

This code has to be run on the console of the website itself after logging in. The first part of the code will loop through all the pages of the list of companies (*# of pages must be manually set*). It will extract the fields/data and append it to a CSV contianing all the companies and their information. Once this code is done running (5-10 seconds with 92 pages), the second part of the code can be run in the console to add a CSV download link to the `<head>` of the page. The CSV will contain the following information for each company: `Title, Company ID, Location, Phone, Fax, Email, Website, Products, Contact Fullname, Contact Role`. 

## `WFF23`
Scraper and Parser for exhibitors of the [2023 Winter Fancy Food Show](https://wff2023.mapyourshow.com/)

To start the process, you will need the 3 python files (`getVendors.py`, `scrape.py`, `parse.py`) and an empty folder titled `pages` (can be changed later on). 

Go to the [exhibitor list page](https://wff2023.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false) and expand the list of all exhibitors and scroll all the way through it to load the content. Afterwords, open the dev console and search for the `<tbody>` that contains the links to all the exhibitors and copy that HTML element. Create an html file in the same folder as the `.py` files and paste the HTML (ex: `vendors.html`). You will then run the following files in order:

### `getVendors.py`
This code will take the HTML pasted from the site and extract all the vendor ids into a `vendors.txt` file. 

How to run: `python3 getVendors.py [HTML file]`

### `scrape.py`
This code will take the list of vendor/exhibitor ids we just extracted and the base url of the site and scrape each exhibitor's page into an output folder. If you have a specific name for the folder you can input that, otherwise it will default to `pages`. Note that the base url in this case is the URL of the exhibitor's page without the ID (ex: https://wff2023.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid=)

How to run: `python3 scrape.py [vendor IDs file] [base url] [optional output folder]`

### `parse.py`
This code will go through each of the pages that were just scraped and parse through them using Python's `BeautifulSoup` package and push all of the companies' information into a `data.json` file. When running this, you'll need to provide the base_url of the website which is the host in this case (ex: https://wff2023.mapyourshow.com)

How to run: `python3 parse.py [base url]`
