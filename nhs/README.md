# NHS Exhibitor Scraper

Scrapes exhibitor data from the NHS Concept to Commerce directory using a 3-step workflow: extract organisation IDs from the list page HTML, fetch full exhibitor data from GraphQL, then parse to CSV.

## Website
- List page: `https://www.nhsconcepttocommerce.com/en-us/exhibit-hall/exhibitor-list.html`

## Workflow

### Step 1: Get Organisation IDs From List HTML
Copy the exhibitor list container HTML from your browser dev tools and save it as `vendors.html` in this folder.

Run:
```bash
uv run getVendors.py vendors.html
```

Output:
- `vendors.txt` - one `organisation_id` (for example `org-23fd1839-e1e3-4a2e-b9f1-b45f8fdc88be`) per line.

### Step 2: Fetch Exhibitor JSON From GraphQL
Run:
```bash
uv run scrape.py vendors.txt eve-e3691757-182e-41e8-a5c2-ec941bc13860 15
```

Arguments:
- `vendors.txt` = file created in step 1
- `eventEditionId` = NHS event edition ID (update if it changes)
- `15` = optional concurrency (default 15)

Output:
- `pages/` directory with one JSON file per exhibitor.

### Step 3: Parse JSON To CSV
Run:
```bash
uv run parse.py pages nhs_exhibitors.csv
```

Output:
- `nhs_exhibitors.csv` with flattened exhibitor data (company profile, contact info, booths, categories, socials, products).

## Notes
- If the event changes year, update the `eventEditionId` used in step 2.
- This scraper uses the same GraphQL endpoint shown in your captured network call: `https://api.reedexpo.com/graphql/`.
