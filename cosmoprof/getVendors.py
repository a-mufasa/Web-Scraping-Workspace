# Gets vendor URLs from Cosmoprof API
import httpx
import sys

HELP_TEXT='''VENDORS GETTER!
Fetches all exhibitor URLs from Cosmoprof API!

USAGE: python3 getVendors.py

Outputs to vendors.txt with one URL per line
'''

def fetch_exhibitors():
    """Fetch all exhibitors from the API"""
    url = 'https://miami-directory.cosmoprofnorthamerica.com/api/v1/search/exhibitors'
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://miami-directory.cosmoprofnorthamerica.com',
        'Referer': 'https://miami-directory.cosmoprofnorthamerica.com/newfront/marketplace/exhibitors',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'x-application': '3',
        'x-lang': 'en',
    }
    
    exhibitor_urls = []
    seen_urls = set()
    page = 1
    limit = 60  # API seems to have a max of 60 per page
    
    print("Fetching exhibitors from API...")
    
    client = httpx.Client(headers=headers, timeout=30)
    
    while True:
        payload = {
            "page": page,
            "limit": limit,
            "nextResult": {}
        }
        
        try:
            response = client.post(url, json=payload)
            
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            data = response.json()
            
            # Cosmoprof API structure: data.list contains exhibitors, data.total has count
            if 'data' not in data or 'list' not in data['data']:
                print(f"Unexpected API response format")
                break
            
            results = data['data']['list']
            
            if not results:
                print(f"No more results at page {page}")
                break
            
            for exhibitor in results:
                # Store only the URL
                exhibitor_url = exhibitor.get('url')
                
                if exhibitor_url and exhibitor_url not in seen_urls:
                    seen_urls.add(exhibitor_url)
                    exhibitor_urls.append(exhibitor_url)
            
            print(f"Page {page}: Found {len(results)} exhibitors (Total: {len(exhibitor_urls)})")
            
            # Check if there are more pages
            total = data['data'].get('total', 0)
            
            if len(exhibitor_urls) >= total:
                print(f"Reached end of results. Total: {len(exhibitor_urls)}")
                break
            
            if len(results) < limit:
                print(f"Reached end of results (fewer results than limit). Total: {len(exhibitor_urls)}")
                break
            
            page += 1
                
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    client.close()
    return exhibitor_urls

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        print(HELP_TEXT)
    else:
        exhibitor_urls = fetch_exhibitors()
        
        if exhibitor_urls:
            with open('vendors.txt', 'w') as f:
                f.write('\n'.join(exhibitor_urls))
            print(f"\n✓ Saved {len(exhibitor_urls)} exhibitor URLs to vendors.txt")
        else:
            print("No exhibitors found!")
