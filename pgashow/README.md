# PGA Show Scraper

Scrapes exhibitor data from PGA Show using the Algolia search API.

## Website
https://www.pgashow.com/

## Usage

Run the scraper to fetch all exhibitors and save to CSV:
```bash
uv run scrape.py
```

Or specify a custom output filename:
```bash
uv run scrape.py my_output.csv
```

**Output:** `pgashow_exhibitors.csv` (or your custom filename)

## Data Collected

The scraper retrieves the following information for each exhibitor:
- Company Name
- Booth Number
- Description
- Website
- Contact Information (email, phone)
- Address (street, city, state, zip, country)
- Social Media (Facebook, Twitter, Instagram, LinkedIn, YouTube)
- Categories
- Object ID and Record Type

## How It Works

The scraper queries the Algolia search API that powers the PGA Show exhibitor directory:
- Automatically handles pagination to retrieve all exhibitors
- Parses JSON responses from the API
- Extracts and formats exhibitor data
- Writes results to a CSV file
