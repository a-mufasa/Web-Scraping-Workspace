import sys
import os
import httpx
import asyncio

HELP_TEXT = '''Async Scraper! Scrapes lists of pages with concurrent requests
USAGE: python3 scrape.py [list to exhids] [base_url] [output (optional)] [concurrency (optional)]

- list to exhids = Literally a .txt file with list of exhibition ids
- base_url = All the url before the exhid. EX: https://wff2025.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid=
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

async def scrape_all(base_url, exhids, output, concurrency):
    """Scrape all pages concurrently"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://wff2025.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    cookies = {
        'CFID': '51997898',
        'CFTOKEN': '3585f8544522eca6-CA55A7C2-C172-DE01-73DE70718AC2B5DF',
        'JSESSIONID': '268F88B625E2BBD8DBEE2F7C5196D0A5.vts',
    }
    
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrency)
    
    async with httpx.AsyncClient(headers=headers, cookies=cookies, timeout=30) as client:
        tasks = []
        
        for exhid in exhids:
            if not exhid.strip():
                continue
            
            name = exhid.replace('/', '_SLASH_')
            output_path = f'{output}{name}.html'
            full_url = base_url + exhid
            
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
        
        with open(sys.argv[1], 'r') as f:
            urls = f.read()
        
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
        
        exhids = [url.strip() for url in urls.split('\n') if url.strip()]
        
        print(f"Found {len(exhids)} pages to scrape...")
        print(f"Using {concurrency} concurrent requests")
        
        # Run the async scraper
        asyncio.run(scrape_all(base_url, exhids, output, concurrency))
        
        print("\nScraping complete!")

