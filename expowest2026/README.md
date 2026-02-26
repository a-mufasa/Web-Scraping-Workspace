# ExpoWest 2026 Exhibitor Scraper

Scrapes exhibitor data from ExpoWest 2026 using their GraphQL API.

## Overview

This scraper collects exhibitor information from ExpoWest 2026, including:
- Company name, type, and description
- Contact information (website, email, phone)
- Booth numbers and hall locations
- Social media profiles (with full URLs)
- Product categories
- Team member counts
- And more custom fields

## Data Source

- **Exhibitor Data**: JSON from https://www.expowest.com/en/exhibitor-list/2026-exhibitor-list.html
- **GraphQL API**: https://attend.expowest.com/api/graphql

## Setup

Make sure you have the required dependencies:

```bash
pip install httpx
```

## Usage

### Step 1: Get Exhibitor IDs

Save the JSON data from the exhibitor list page to a file (e.g., `exhibitors.json`), then extract the exhibitor IDs:

```bash
uv run getVendors.py exhibitors.json
```

This will create a `exhibitors.txt` file with one exhibitor ID per line.

### Step 2: Scrape Exhibitor Data

Run the scraper to fetch data for all exhibitors via GraphQL:

```bash
uv run scrape.py exhibitors.txt
```

Optional: Specify concurrency (default is 10):

```bash
uv run scrape.py exhibitors.txt 20
```

This saves raw JSON responses to `pages/` directory.

### Step 3: Parse to CSV

Convert the JSON files to a CSV:

```bash
uv run parse.py pages expowest2026_exhibitors.csv
```

Optional: Parse only a subset for testing:

```bash
uv run parse.py pages expowest2026_exhibitors.csv 50
```

### Output

- **JSON Files**: `pages/*.json` - Raw GraphQL responses saved as JSON files
- **CSV File**: `expowest2026_exhibitors.csv` - Contains all exhibitor data in a flat CSV format

## GraphQL Query

The scraper uses the persisted query hash from the ExpoWest event app:
- Operation: `EventExhibitorDetailsViewQuery`
- Hash: `11891ad980c93f089fb1727527507145684eaffa27463f41cdfc31f2af2f6779`
- Event ID: `RXZlbnRfMzAxMDc4Nw==` (ExpoWest 2026)

## Data Fields

The CSV includes:
- `exhibitor_url`: Full URL to exhibitor page
- `name`, `type`, `website`, `email`, `phone`, `description`
- `booth_numbers`, `hall`
- `country`, `state`, `city`, `street`, `zip_code`
- `product_category`, `first_time_exhibitor`, `fresh_ideas_organic`, `us_state_canadian_province`
- `twitter`, `facebook`, `instagram`, `linkedin`, `youtube` (full URLs)
- `logo_url`, `beacon_url`
- `team_members_count`

## Notes

- The scraper respects rate limits with controlled concurrency
- Failed requests are logged but don't stop the scraper
- JSON backups allow for re-parsing without re-scraping
- Exhibitor IDs are base64-encoded strings (e.g., `RXhoaWJpdG9yXzIzNTg1MzM=`)
- Social media URLs are automatically formatted (e.g., `twitter.com/username`)
- All fields have safe defaults to prevent CSV errors
