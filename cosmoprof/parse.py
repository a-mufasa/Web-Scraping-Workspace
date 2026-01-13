import sys
import json
import csv
import httpx
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup

HELP_TEXT = '''Parser! Extracts data from exhibitor HTML pages
USAGE: python3 parse.py [pages_dir] [output_csv] [limit (optional)]

- pages_dir = directory containing downloaded HTML files (from scrape.py)
- output_csv = output CSV file name
- limit (optional) = number of files to parse for testing; Default = all files
'''

def extract_next_data(html):
    """Extract data from __NEXT_DATA__ script tag"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the __NEXT_DATA__ script tag
    script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
    
    if not script_tag:
        return None
    
    try:
        data = json.loads(script_tag.string)
        
        # Extract exhibitor data from props.pageProps.controlItem
        if 'props' in data and 'pageProps' in data['props'] and 'controlItem' in data['props']['pageProps']:
            return data['props']['pageProps']['controlItem']
        
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

async def fetch_all_contacts(exhibitor_ids):
    """Fetch contacts for all exhibitors concurrently"""
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://miami-directory.cosmoprofnorthamerica.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'x-application': '3',
        'x-lang': 'en',
    }
    
    contacts_dict = {}
    
    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        # Create tasks for all exhibitor IDs and fetch concurrently
        tasks = [fetch_contacts(client, exhibitor_id) for exhibitor_id in exhibitor_ids]
        
        # Fetch all contacts concurrently using gather
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results back to exhibitor IDs
        for exhibitor_id, result in zip(exhibitor_ids, results):
            if isinstance(result, Exception):
                contacts_dict[exhibitor_id] = []
            else:
                contacts_dict[exhibitor_id] = result
    
    return contacts_dict

async def fetch_contacts(client, exhibitor_id):
    """Fetch contact information from API"""
    url = 'https://miami-directory.cosmoprofnorthamerica.com/api/v1/exhibitors/contacts'
    
    payload = {
        "id": str(exhibitor_id),
        "limit": 12,
        "page": 1
    }
    
    try:
        response = await client.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'list' in data['data']:
                contacts = data['data']['list']
                return contacts
            else:
                return []
        else:
            return []
    except Exception as e:
        return []

def parse_page(html_file, contacts_data):
    """Parse a single exhibitor page"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    exhibitor_data = extract_next_data(html)
    
    if not exhibitor_data:
        return None
    
    # Extract booth information
    booths = []
    if 'stands' in exhibitor_data and exhibitor_data['stands']:
        for stand_group in exhibitor_data['stands']:
            hall = stand_group.get('hall', '')
            stand = stand_group.get('stand', '')
            if hall and stand:
                booths.append(f"{hall} - {stand}")
    
    booth_info = '; '.join(booths) if booths else ''
    
    # Extract categories and filter out group headers
    categories = []
    category_headers = ['FINISHED PRODUCTS & SERVICES CATEGORIES', 'SUPPLY CHAIN CATEGORIES', 'PRODUCT POSITIONING']
    if 'categories' in exhibitor_data and exhibitor_data['categories']:
        for cat in exhibitor_data['categories']:
            cat_name = cat.get('name', '')
            # Filter out category group headers
            if cat_name and cat_name not in category_headers:
                categories.append(cat_name)
    
    # Extract products
    products = []
    if 'products' in exhibitor_data and exhibitor_data['products']:
        products = [prod.get('name', '') for prod in exhibitor_data['products']]
    
    # Clean the about field - strip HTML tags
    about_text = exhibitor_data.get('about', '')
    if about_text:
        # Use BeautifulSoup to strip HTML and get clean text
        soup = BeautifulSoup(about_text, 'html.parser')
        about_text = soup.get_text(separator=' ', strip=True)
    
    # Get contacts from pre-fetched data
    exhibitor_id = exhibitor_data.get('id')
    contacts = contacts_data.get(exhibitor_id, []) if exhibitor_id else []
    
    # Format contacts
    contact_names = []
    contact_positions = []
    contact_phones = []
    contact_emails = []
    
    for contact in contacts:
        first_name = contact.get('firstName', '')
        last_name = contact.get('lastName', '')
        name = f"{first_name} {last_name}".strip()
        if name:
            contact_names.append(name)
        
        position = contact.get('position', '')
        if position:
            contact_positions.append(position)
        
        phone = contact.get('phone', '') or contact.get('company_phone', '')
        if phone:
            contact_phones.append(phone)
        
        email = contact.get('email', '')
        if email:
            contact_emails.append(email)
    
    return {
        'url': f"https://miami-directory.cosmoprofnorthamerica.com/newfront/exhibitor/{exhibitor_data.get('url', '')}",
        'exhibitor_id': exhibitor_data.get('id', ''),
        'company_name': exhibitor_data.get('name', ''),
        'booth_number': booth_info,
        'about': about_text,
        'categories': ', '.join(categories),
        'products': ', '.join(products),
        'address': exhibitor_data.get('address', ''),
        'city': exhibitor_data.get('city', ''),
        'region': exhibitor_data.get('region', ''),
        'country': exhibitor_data.get('country', ''),
        'zip': exhibitor_data.get('zip', ''),
        'website': exhibitor_data.get('website', ''),
        'phone': exhibitor_data.get('phone', ''),
        'logo': exhibitor_data.get('logo', ''),
        'facebook': exhibitor_data.get('acc_fb', ''),
        'instagram': exhibitor_data.get('acc_ig', ''),
        'twitter': exhibitor_data.get('acc_tw', ''),
        'linkedin': exhibitor_data.get('acc_in', ''),
        'youtube': exhibitor_data.get('acc_yt', ''),
        'contact_names': '; '.join(contact_names),
        'contact_positions': '; '.join(contact_positions),
        'contact_phones': '; '.join(contact_phones),
        'contact_emails': '; '.join(contact_emails),
    }

def parse_all(pages_dir, output_csv, limit=None):
    """Parse all HTML files and write to CSV"""
    pages_path = Path(pages_dir)
    
    if not pages_path.exists():
        print(f"Error: Directory {pages_dir} does not exist")
        return
    
    html_files = list(pages_path.glob('*.html'))
    
    if not html_files:
        print(f"No HTML files found in {pages_dir}")
        return
    
    # Limit number of files if specified
    if limit and limit > 0:
        html_files = html_files[:limit]
        print(f"Limited to {len(html_files)} files for testing\n")
    
    print(f"Found {len(html_files)} HTML files to parse\n")
    
    # First, extract all exhibitor IDs from HTML files
    print("Extracting exhibitor IDs...")
    exhibitor_ids = []
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        exhibitor_data = extract_next_data(html)
        if exhibitor_data and exhibitor_data.get('id'):
            exhibitor_ids.append(exhibitor_data['id'])
    
    print(f"Found {len(exhibitor_ids)} exhibitor IDs\n")
    
    # Fetch all contacts concurrently
    print("Fetching contacts from API...")
    contacts_data = asyncio.run(fetch_all_contacts(exhibitor_ids))
    print(f"Fetched contacts for {len(contacts_data)} exhibitors\n")
    
    # Now parse all files
    print("Parsing HTML files...")
    results = []
    
    for i, html_file in enumerate(html_files, 1):
        result = parse_page(html_file, contacts_data)
        
        if result:
            results.append(result)
        
        if i % 25 == 0 or i == len(html_files):
            print(f"Parsed {i} out of {len(html_files)} files")
    
    # Write to CSV
    if results:
        fieldnames = [
            'url',
            'exhibitor_id',
            'company_name',
            'booth_number',
            'about',
            'categories',
            'products',
            'address',
            'city',
            'region',
            'country',
            'zip',
            'website',
            'phone',
            'logo',
            'facebook',
            'instagram',
            'twitter',
            'linkedin',
            'youtube',
            'contact_names',
            'contact_positions',
            'contact_phones',
            'contact_emails',
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow(result)
        
        print(f"\n✓ Saved {len(results)} exhibitors to {output_csv}")
    else:
        print("\nNo results to write!")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(HELP_TEXT)
    else:
        pages_dir = sys.argv[1]
        output_csv = sys.argv[2]
        
        # Optional limit parameter
        limit = None
        if len(sys.argv) >= 4:
            try:
                limit = int(sys.argv[3])
            except ValueError:
                print(f"Warning: Invalid limit value '{sys.argv[3]}', parsing all files")
        
        parse_all(pages_dir, output_csv, limit)
        
        print("\nParsing complete!")
