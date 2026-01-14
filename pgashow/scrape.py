import httpx
import csv
import sys

HELP_TEXT = '''PGA Show Exhibitor Scraper - Fetches data from Algolia API
USAGE: python3 scrape.py [output_csv]

- output_csv = name of output CSV file (default: pgashow_exhibitors.csv)
'''

def get_safe(data, *keys, default=''):
    """Safely get nested dictionary values"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data if data is not None else default

def scrape_algolia():
    """Scrape all exhibitors from PGA Show Algolia API"""
    
    url = 'https://xd0u5m6y4r-dsn.algolia.net/1/indexes/evt-f099659d-adb6-4cfb-9673-93482d1d5223-index/query'
    
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://www.pgashow.com',
        'Referer': 'https://www.pgashow.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    
    params = {
        'x-algolia-agent': 'Algolia for JavaScript (3.35.1); Browser',
        'x-algolia-application-id': 'XD0U5M6Y4R',
        'x-algolia-api-key': 'd5cd7d4ec26134ff4a34d736a7f9ad47'
    }
    
    all_exhibitors = []
    page = 0
    
    print("Starting to scrape PGA Show exhibitors from Algolia API...\n")
    
    with httpx.Client(timeout=30) as client:
        while True:
            # Build the request payload
            payload = {
                "params": f"query=&page={page}&filters=recordType%3Aexhibitor%20AND%20locale%3Aen-us%20AND%20eventEditionId%3Aeve-419819ac-309e-4ba7-a49d-3f0c8dbd7d02&facetFilters=&optionalFilters=%5B%5D"
            }
            
            try:
                response = client.post(url, params=params, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                hits = data.get('hits', [])
                if not hits:
                    print(f"No more results on page {page}")
                    break
                
                all_exhibitors.extend(hits)
                print(f"Page {page}: Retrieved {len(hits)} exhibitors (Total: {len(all_exhibitors)})")
                
                # Check if we've reached the last page
                nb_pages = data.get('nbPages', 0)
                if page >= nb_pages - 1:
                    print(f"Reached last page ({nb_pages} total pages)")
                    break
                
                page += 1
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
    
    return all_exhibitors

def parse_exhibitor(hit):
    """Parse exhibitor data from Algolia hit"""
    return {
        'Company Name': get_safe(hit, 'companyName'),
        'Exhibitor Name': get_safe(hit, 'exhibitorName'),
        'Booth Number': get_safe(hit, 'standReference'),
        'Description': get_safe(hit, 'exhibitorDescription'),
        'Show Objective': get_safe(hit, 'showObjective'),
        'Website': get_safe(hit, 'website'),
        'Email': get_safe(hit, 'email'),
        'Phone': get_safe(hit, 'phone'),
        'Country': get_safe(hit, 'countryName'),
        'Represented Brands': ', '.join(get_safe(hit, 'representedBrands', default=[])),
        'Product Categories': ', '.join(get_safe(hit, 'ppsAnswers', default=[])),
        'Exhibitor Features': ', '.join(get_safe(hit, 'exhibitorFeatures', default=[])),
        'Logo URL': get_safe(hit, 'logo'),
        'Cover Image URL': get_safe(hit, 'coverImage'),
        'Is New': get_safe(hit, 'isNew'),
        'Package ID': get_safe(hit, 'packageId'),
        'Exhibitor Type ID': get_safe(hit, 'exhibitorTypeId'),
        'Record Type': get_safe(hit, 'recordType'),
        'ID': get_safe(hit, 'id'),
        'Object ID': get_safe(hit, 'objectID'),
    }

def write_csv(exhibitors, output_file):
    """Write exhibitor data to CSV"""
    if not exhibitors:
        print("No exhibitors to write")
        return
    
    # Parse all exhibitors
    parsed_data = [parse_exhibitor(hit) for hit in exhibitors]
    
    # Get all unique keys
    fieldnames = list(parsed_data[0].keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)
    
    print(f"\n✓ Saved {len(parsed_data)} exhibitors to {output_file}")

if __name__ == '__main__':
    output_file = 'pgashow_exhibitors.csv'
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print(HELP_TEXT)
            sys.exit(0)
        output_file = sys.argv[1]
    
    exhibitors = scrape_algolia()
    write_csv(exhibitors, output_file)
