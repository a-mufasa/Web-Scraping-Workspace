from bs4 import BeautifulSoup
import os
import csv
import re

def extract_exhibitor_data(html_content):
    """
    Extract exhibitor information from HTML content.
    Returns a dictionary with the extracted data.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    data = {
        'company_name': '',
        'exhibitor_type': '',
        'booth_number': '',
        'description': '',
        'product_categories': '',
        'has_new_product': '',
        'state': '',
        'country': '',
        'website': '',
        'location': '',
        'linkedin': '',
        'instagram': '',
        'facebook': '',
        'twitter': '',
    }
    
    # Extract company name from h1 tag with class "sc-5973f5f6-7"
    company_h1 = soup.find('h1', class_=re.compile(r'sc-5973f5f6-7'))
    if company_h1:
        data['company_name'] = company_h1.get_text(strip=True)
    
    # Extract exhibitor type from h2 with class matching pattern
    exhibitor_type_h2 = soup.find('h2', class_=re.compile(r'sc-5973f5f6-8'))
    if exhibitor_type_h2:
        data['exhibitor_type'] = exhibitor_type_h2.get_text(strip=True)
    
    # Extract booth number from span with class "sc-16aa256c-0"
    booth_span = soup.find('span', class_=re.compile(r'sc-16aa256c-0'))
    if booth_span:
        data['booth_number'] = booth_span.get_text(strip=True)
    
    # Extract description from the Information section
    description_div = soup.find('div', class_=re.compile(r'sc-88662468-0'))
    if description_div:
        data['description'] = description_div.get_text(strip=True)
    
    # Extract information fields (Has New Product, State, Country, Product categories, etc.)
    info_sections = soup.find_all('div', class_=re.compile(r'sc-b0617814-0'))
    for section in info_sections:
        label_div = section.find('div', class_=re.compile(r'sc-b0617814-1'))
        value_div = section.find('div', class_=re.compile(r'sc-b0617814-2'))
        
        if label_div and value_div:
            label = label_div.get_text(strip=True)
            value = value_div.get_text(strip=True)
            
            if 'New Product' in label:
                data['has_new_product'] = value
            elif 'State' in label:
                data['state'] = value
            elif 'Country' in label:
                data['country'] = value
            elif 'Product categories' in label or 'Product Categories' in label:
                data['product_categories'] = value
    
    # Extract website from Contact details section
    # Look for website links (excluding Google Maps)
    contact_links = soup.find_all('a', href=re.compile(r'^https?://'))
    for link in contact_links:
        href = link.get('href', '')
        if 'google.com/maps' not in href and not data['website']:
            # Check if it's in a contact details section by looking at nearby elements
            parent = link.find_parent('div', class_=re.compile(r'sc-be6fa72a-1'))
            if parent:
                data['website'] = href
                break
    
    # Extract location from Google Maps link
    maps_link = soup.find('a', href=re.compile(r'google\.com/maps'))
    if maps_link:
        location_span = maps_link.find('span')
        if location_span:
            data['location'] = location_span.get_text(strip=True)
    
    # Extract social media links
    social_links = soup.find_all('a', {'target': '_blank', 'rel': 'noopener noreferrer'})
    for link in social_links:
        title = link.get('title', '').lower()
        href = link.get('href', '')
        
        if 'linkedin' in title or 'linkedin.com' in href:
            data['linkedin'] = href
        elif 'instagram' in title or 'instagram.com' in href:
            data['instagram'] = href
        elif 'facebook' in title or 'facebook.com' in href:
            data['facebook'] = href
        elif 'twitter' in title or 'twitter.com' in href or 'x.com' in href:
            data['twitter'] = href
    
    return data


def parse_all_pages():
    """
    Parse all HTML files in the pages directory and create a CSV file.
    """
    pages_dir = 'pages'
    output_csv = 'specialtyfood_exhibitors.csv'
    
    # Get all HTML files in the pages directory
    html_files = [f for f in os.listdir(pages_dir) if f.endswith('.html')]
    
    print(f"Found {len(html_files)} HTML files to parse...")
    
    # Prepare CSV
    fieldnames = [
        'url',
        'company_name',
        'exhibitor_type',
        'booth_number',
        'description',
        'product_categories',
        'has_new_product',
        'state',
        'country',
        'website',
        'location',
        'linkedin',
        'instagram',
        'facebook',
        'twitter',
    ]
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, filename in enumerate(html_files, 1):
            try:
                # Extract exhibitor ID from filename
                exhibitor_id = filename.replace('.html', '')
                
                # Read HTML file
                filepath = os.path.join(pages_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Extract data
                data = extract_exhibitor_data(html_content)
                data['url'] = f'https://events.specialtyfood.com/event/winter-fancyfaire/exhibitor/{exhibitor_id}'
                
                # Write to CSV
                writer.writerow(data)
                
                print(f"[{i}/{len(html_files)}] Parsed {data['company_name'] or exhibitor_id}")
                
            except Exception as e:
                print(f"Error parsing {filename}: {str(e)}")
                continue
    
    print(f"\nParsing complete! Data saved to {output_csv}")


if __name__ == '__main__':
    parse_all_pages()
