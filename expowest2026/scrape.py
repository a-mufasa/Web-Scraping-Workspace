import sys
import httpx
import asyncio
import json
from pathlib import Path

HELP_TEXT = """Async GraphQL Scraper for ExpoWest 2026!
Downloads exhibitor data via GraphQL API and saves to JSON files

USAGE: uv run scrape.py [vendors_file] [concurrency (optional)]

ARGUMENTS
- vendors_file = text file with exhibitor IDs (from getVendors.py)
- concurrency (optional) = number of concurrent requests; Default to 10

Saves JSON responses to pages/ directory
Use parse.py to convert JSON files to CSV
"""

# GraphQL query hash and operation from HAR file
GRAPHQL_URL = "https://attend.expowest.com/api/graphql"
EVENT_ID = "RXZlbnRfMzAxMDc4Nw=="  # ExpoWest 2026 event ID

GRAPHQL_OPERATION = {
    "operationName": "EventExhibitorDetailsViewQuery",
    "extensions": {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "11891ad980c93f089fb1727527507145684eaffa27463f41cdfc31f2af2f6779",
        }
    },
}


async def scrape_exhibitor(client, exhibitor_id, semaphore):
    """Fetch a single exhibitor's data via GraphQL"""
    async with semaphore:
        try:
            payload = {
                **GRAPHQL_OPERATION,
                "variables": {
                    "withEvent": True,
                    "skipMeetings": True,
                    "exhibitorId": exhibitor_id,
                    "eventId": EVENT_ID,
                },
            }

            response = await client.post(GRAPHQL_URL, json=[payload], timeout=30)

            if response.status_code == 200:
                data = response.json()
                return (exhibitor_id, data)
            else:
                print(f"Failed to fetch {exhibitor_id}: HTTP {response.status_code}")
                return (exhibitor_id, None)
        except Exception as e:
            print(f"Error fetching {exhibitor_id}: {e}")
            return (exhibitor_id, None)


async def scrape_all(exhibitor_ids, concurrency):
    """Scrape all exhibitors concurrently"""
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://attend.expowest.com",
        "referer": "https://attend.expowest.com/",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "x-client-origin": "attend.expowest.com",
        "x-client-platform": "Event App",
        "x-client-version": "2.310.6",
        "x-content-language": "en_US",
        "x-feature-flags": "fixBackwardPaginationOrder",
    }

    semaphore = asyncio.Semaphore(concurrency)

    # Create pages directory for JSON responses
    pages_dir = Path("pages")
    pages_dir.mkdir(exist_ok=True)

    async with httpx.AsyncClient(
        headers=headers, timeout=30, follow_redirects=True
    ) as client:
        tasks = []

        for exhibitor_id in exhibitor_ids:
            task = scrape_exhibitor(client, exhibitor_id, semaphore)
            tasks.append(task)

        print(
            f"Starting to scrape {len(tasks)} exhibitors with {concurrency} concurrent requests...\n"
        )

        completed = 0
        saved = 0

        for coro in asyncio.as_completed(tasks):
            exhibitor_id, json_data = await coro

            if json_data:
                # Save JSON response
                filename = pages_dir / f"{exhibitor_id}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2)
                saved += 1

            completed += 1
            if completed % 25 == 0 or completed == len(tasks):
                print(
                    f"Completed {completed} out of {len(tasks)} exhibitors ({saved} saved)"
                )

        print(f"\n✓ Saved {saved} JSON files to pages/ directory")
        print(
            f"\nRun 'python3 parse.py pages expowest2026_exhibitors.csv' to generate CSV"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP_TEXT)
    else:
        vendors_file = sys.argv[1]

        try:
            concurrency = int(sys.argv[2])
        except (IndexError, ValueError):
            concurrency = 10

        # Load exhibitor IDs from text file
        with open(vendors_file, "r") as f:
            exhibitor_ids = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(exhibitor_ids)} exhibitor IDs from {vendors_file}")
        print(f"Using {concurrency} concurrent requests\n")

        # Run the async scraper
        asyncio.run(scrape_all(exhibitor_ids, concurrency))

        print("\nScraping complete!")
