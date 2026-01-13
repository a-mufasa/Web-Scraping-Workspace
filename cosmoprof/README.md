# Cosmoprof North America Scraper

Scrapes exhibitor data from Cosmoprof North America marketplace using a 3-step workflow: fetch URLs, download pages, parse data.

## Website
https://miami-directory.cosmoprofnorthamerica.com/newfront/marketplace/exhibitors

## Workflow

### Step 1: Get Vendor URLs
Fetch all exhibitor URL slugs from the API:
```bash
uv run getVendors.py
```

**Output:** `vendors.txt` - Contains one exhibitor URL slug per line

### Step 2: Scrape Pages
Download all exhibitor HTML pages:
```bash
uv run scrape.py vendors.txt https://miami-directory.cosmoprofnorthamerica.com/newfront/exhibitor/ 20
```

**Output:** `pages/` directory - Contains all downloaded HTML pages

**Note:** The third parameter (20) is the number of concurrent requests - adjust for faster/slower scraping.

### Step 3: Parse Data
Extract data from HTML pages and fetch contact info from API:
```bash
uv run parse.py pages/ cosmoprof_exhibitors.csv
```

**Output:** `cosmoprof_exhibitors.csv` - Contains all exhibitor details including:
- Company information (name, about, booth, website, phone, address)
- Social media (Facebook, Instagram, Twitter, LinkedIn, YouTube)
- Products and categories
- Contact information (names, positions, phones, emails)

## Data Sources
- **HTML Pages**: Most exhibitor data is extracted from the `__NEXT_DATA__` script tag embedded in each page
- **Contacts API**: Contact information is fetched via POST request to `/api/v1/exhibitors/contacts`

