import sys
import httpx
import asyncio
from pathlib import Path

HELP_TEXT = '''Async Scraper! Downloads exhibitor pages to pages/ folder
USAGE: python3 scrape.py [vendors_file] [base_url] [concurrency (optional)]

- vendors_file = text file with exhibitor URLs (from getVendors.py)
- base_url = Base URL for exhibitor pages. EX: https://miami-directory.cosmoprofnorthamerica.com/newfront/exhibitor/
- concurrency (optional) = number of concurrent requests; Default to 20
'''

async def scrape_page(client, url, slug, semaphore):
    """Download a single exhibitor page"""
    async with semaphore:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                return (slug, response.text)
            else:
                print(f"Failed to fetch {slug}: HTTP {response.status_code}")
                return (slug, None)
        except Exception as e:
            print(f"Error fetching {slug}: {e}")
            return (slug, None)

async def scrape_all(urls, base_url, concurrency):
    """Scrape all exhibitor pages concurrently"""
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    
    # Basic cookies to make the site think we're a real browser
    cookies = {
        'lang': 'en',
        'initiated': 'true',
    }
    
    semaphore = asyncio.Semaphore(concurrency)
    
    # Create pages directory if it doesn't exist
    pages_dir = Path('pages')
    pages_dir.mkdir(exist_ok=True)
    
    async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=30, follow_redirects=True) as client:
        tasks = []
        
        for url_slug in urls:
            full_url = f"{base_url}/{url_slug}"
            task = scrape_page(client, full_url, url_slug, semaphore)
            tasks.append(task)
        
        print(f"Starting to scrape {len(tasks)} exhibitors with {concurrency} concurrent requests...\n")
        
        completed = 0
        saved = 0
        
        for coro in asyncio.as_completed(tasks):
            slug, html = await coro
            
            if html:
                # Save HTML to file
                filename = pages_dir / f"{slug}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                saved += 1
            
            completed += 1
            if completed % 25 == 0 or completed == len(tasks):
                print(f'Completed {completed} out of {len(tasks)} exhibitors ({saved} saved)')
        
        print(f"\n✓ Saved {saved} pages to pages/ directory")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(HELP_TEXT)
    else:
        vendors_file = sys.argv[1]
        base_url = sys.argv[2].rstrip('/')
        
        try:
            concurrency = int(sys.argv[3])
        except (IndexError, ValueError):
            concurrency = 20
        
        # Load exhibitor URLs from text file
        with open(vendors_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(urls)} exhibitor URLs from {vendors_file}")
        print(f"Base URL: {base_url}")
        print(f"Using {concurrency} concurrent requests\n")
        
        # Run the async scraper
        asyncio.run(scrape_all(urls, base_url, concurrency))
        
        print("\nScraping complete!")
