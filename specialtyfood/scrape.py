import sys
import os
import httpx
import asyncio
from bs4 import BeautifulSoup
import re

HELP_TEXT = '''Async Scraper! Scrapes exhibitor pages from vendors.html with concurrent requests
USAGE: python3 scrape.py [vendors_html] [base_url] [output (optional)] [concurrency (optional)]

- vendors_html = HTML file containing all exhibitor links
- base_url = Base URL for the event. EX: https://events.specialtyfood.com
- output (optional) = the name of the folder to store in; Default to pages
- concurrency (optional) = number of concurrent requests; Default to 10
'''

async def scrape_page(client, url, output_path, semaphore):
    """Scrape a single page with semaphore control"""
    async with semaphore:
        if os.path.exists(output_path):
            return None
        
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return url, True
            else:
                print(f"Failed to fetch {url}: HTTP {response.status_code}")
                return url, False
        except httpx.RequestError as e:
            print(f"Error fetching {url}: {e}")
            return url, False
        except Exception as e:
            print(f"Unexpected error fetching {url}: {e}")
            return url, False

async def scrape_all(base_url, exhibitor_urls, output, concurrency):
    """Scrape all pages concurrently"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrency)
    
    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        tasks = []
        
        for url in exhibitor_urls:
            # Extract exhibitor ID from URL for filename
            match = re.search(r'/exhibitor/([^/]+)$', url)
            if match:
                exhibitor_id = match.group(1)
                name = exhibitor_id
            else:
                name = url.replace('/', '_SLASH_')
            
            output_path = f'{output}{name}.html'
            full_url = base_url + url
            
            task = scrape_page(client, full_url, output_path, semaphore)
            tasks.append(task)
        
        # Run all tasks concurrently with progress updates
        print(f"Starting to scrape {len(tasks)} pages with {concurrency} concurrent requests...")
        
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            completed += 1
            if completed % 25 == 0 or completed == len(tasks):
                print(f'Completed {completed} out of {len(tasks)} pages')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(HELP_TEXT)
    else:
        base_url = sys.argv[2]
        
        # Read and parse the vendors HTML file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all exhibitor links
        exhibitor_links = soup.find_all('a', href=re.compile(r'/event/winter-fancyfaire/exhibitor/'))
        
        # Extract unique exhibitor URLs
        exhibitor_urls = set()
        for link in exhibitor_links:
            href = link.get('href')
            if href:
                exhibitor_urls.add(href)
        
        exhibitor_urls = list(exhibitor_urls)
        
        try:
            output = sys.argv[3]
            if not output.endswith('/'):
                output += '/'
        except IndexError:
            output = 'pages/'
        
        try:
            concurrency = int(sys.argv[4])
        except (IndexError, ValueError):
            concurrency = 10
        
        if not os.path.exists(output):
            os.makedirs(output)
        
        print(f"Found {len(exhibitor_urls)} unique exhibitor pages to scrape...")
        print(f"Using {concurrency} concurrent requests")
        
        # Run the async scraper
        asyncio.run(scrape_all(base_url, exhibitor_urls, output, concurrency))
        
        print("\nScraping complete!")
