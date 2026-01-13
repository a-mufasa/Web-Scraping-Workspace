from bs4 import BeautifulSoup
import os
import csv
import re
import sys
import json

HELP_TEXT = '''Parser for MapYourShow 2026 (exh-details-v3)
USAGE: python3 parse-2026.py [base_url]

ARGUMENTS:
- base_url: The host of the site. EX: https://tfny2026.mapyourshow.com

It reads pages from the pages/ dir, and outputs to exhibitors_2026.csv
'''


def extract_exhibitor_data(html_content, page_id, base_url):
    """
    Extract exhibitor information from HTML content (exh-details-v3 format).
    Returns a dictionary with the extracted data.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Focus on the main exh-details section
    main_section = soup.find('main', id='exhdetails', class_=re.compile(r'exh-details-v3'))
    if not main_section:
        main_section = soup  # Fallback to full document
    
    data = {
        'url': f"{base_url}/8_0/exhibitor/exhibitor-details.cfm?exhid={page_id}",
        'exhibitor_id': page_id,
        'company_name': '',
        'booth_number': '',
        'booth_url': '',
        'logo_url': '',
        'description': '',
        'address': '',
        'city': '',
        'state': '',
        'zip_code': '',
        'country': '',
        'website': '',
        'phone': '',
        'fax': '',
        'email': '',
        'facebook': '',
        'twitter': '',
        'instagram': '',
        'linkedin': '',
        'youtube': '',
        'categories': '',
    }
    
    # Extract company name from h1 or meta tag
    name_tag = main_section.find('h1', class_=re.compile(r'(exhibitor[-_\s]?name|mr3-m)', re.I))
    if name_tag:
        data['company_name'] = name_tag.get_text(strip=True)
    else:
        # Try meta tag
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get("content"):
            title_parts = meta_title["content"].split(" | ")
            if len(title_parts) >= 2:
                data['company_name'] = title_parts[1].strip()
            else:
                data['company_name'] = title_parts[0].strip()
    
    # Extract logo URL
    logo_tag = main_section.find('img', {'class': re.compile(r'logo', re.I)}) or \
               main_section.find('img', {'id': re.compile(r'logo', re.I)})
    if logo_tag and logo_tag.get("src"):
        src = logo_tag["src"].strip()
        if src and src != '/8_0/assets/imgs/1x1.gif':
            data['logo_url'] = base_url + src if src.startswith("/") else src
    
    # Extract booth number and URL - look for Vue data first
    script_tags = soup.find_all('script', string=re.compile(r'boothURL|newfloorplanlink'))
    booth_found = False
    for script_tag in script_tags:
        if script_tag.string:
            # Look for booth data in Vue component
            booth_match = re.search(r'booth:\s*"([^"]+)"', script_tag.string)
            booth_url_match = re.search(r'boothURL:\s*"([^"]+)"', script_tag.string)
            
            if booth_match:
                data['booth_number'] = booth_match.group(1).replace("\\/", "/")
                booth_found = True
            if booth_url_match:
                booth_url = booth_url_match.group(1).replace("\\/", "/")
                data['booth_url'] = base_url + booth_url if booth_url.startswith("/") else booth_url
                booth_found = True
    
    # Fallback to HTML if not found in script
    if not booth_found:
        booth_tag = main_section.find('a', id="newfloorplanlink") or \
                    main_section.find('a', id=re.compile(r'floorplan', re.I))
        if booth_tag:
            booth_text = booth_tag.get_text(separator=" ", strip=True)
            if booth_text:
                data['booth_number'] = booth_text.replace("\u2014", "-").replace("—", "-")
            href = booth_tag.get("href")
            if href:
                data['booth_url'] = base_url + href if href.startswith("/") else href
    
    # Extract contact info from Vue.js contactinfov3 component
    script_tags = soup.find_all('script', string=re.compile(r'contactinfov3'))
    for script_tag in script_tags:
        if script_tag.string:
            script_content = script_tag.string
            
            # Extract address data
            address_match = re.search(r'addressValues:\s*({[^}]+})', script_content)
            if address_match:
                try:
                    address_json = address_match.group(1).replace("\\/", "/")
                    address_data = json.loads(address_json)
                    
                    address_parts = []
                    if address_data.get('ADDRESS1'):
                        address_parts.append(address_data['ADDRESS1'])
                    if address_data.get('ADDRESS2'):
                        address_parts.append(address_data['ADDRESS2'])
                    if address_data.get('ADDRESS3'):
                        address_parts.append(address_data['ADDRESS3'])
                    
                    data['address'] = ', '.join(filter(None, address_parts))
                    data['city'] = address_data.get('CITY', '')
                    data['state'] = address_data.get('STATE', '')
                    data['zip_code'] = address_data.get('ZIP', '')
                    data['country'] = address_data.get('COUNTRY', '')
                except:
                    pass
            
            # Extract website
            website_match = re.search(r'websiteValue:\s*"([^"]*)"', script_content)
            if website_match and website_match.group(1):
                data['website'] = website_match.group(1).replace("\\/", "/")
            
            # Extract phone
            phone_match = re.search(r'phoneValue:\s*"([^"]*)"', script_content)
            if phone_match and phone_match.group(1):
                data['phone'] = phone_match.group(1)
            
            # Extract fax
            fax_match = re.search(r'faxValue:\s*"([^"]*)"', script_content)
            if fax_match and fax_match.group(1):
                data['fax'] = fax_match.group(1)
            
            # Extract social media
            instagram_match = re.search(r'instagramValue:\s*"([^"]*)"', script_content)
            if instagram_match and instagram_match.group(1):
                data['instagram'] = instagram_match.group(1).replace("\\/", "/")
            
            facebook_match = re.search(r'facebookValue:\s*"([^"]*)"', script_content)
            if facebook_match and facebook_match.group(1):
                data['facebook'] = facebook_match.group(1).replace("\\/", "/")
            
            twitter_match = re.search(r'twitterValue:\s*"([^"]*)"', script_content)
            if twitter_match and twitter_match.group(1):
                data['twitter'] = twitter_match.group(1).replace("\\/", "/")
            
            linkedin_match = re.search(r'linkedInValue:\s*"([^"]*)"', script_content)
            if linkedin_match and linkedin_match.group(1):
                data['linkedin'] = linkedin_match.group(1).replace("\\/", "/")
    
    # Extract description from HTML
    desc_tag = main_section.find(lambda tag: tag.name in ["p", "div"] and tag.get("class") and 
                                any(re.search(r"(description|read[-]?more|showcase[-]?desc)", cls, re.I) 
                                    for cls in tag.get("class", [])))
    if desc_tag:
        description = desc_tag.get_text(separator=" ", strip=True)
        # Clean up special characters
        description = description.replace("\u00a9", "").replace("\u2019", "'") \
            .replace("\u201c", '"').replace("\u201d", '"') \
            .replace("\u2013", "-").replace("\u2014", "-") \
            .replace("\n", " ").replace("\r", "")
        data['description'] = description
    
    # Extract categories from script tag
    script_tag = soup.find("script", string=re.compile(r"productcategories"))
    if script_tag and script_tag.string:
        cat_match = re.search(r"productcategories:\s*(\[[^\]]+\])", script_tag.string, re.MULTILINE | re.DOTALL)
        if cat_match:
            try:
                categories_raw = cat_match.group(1).replace("'", '"')
                categories = json.loads(categories_raw)
                # Extract just the display names
                category_names = [cat.get('display', '') for cat in categories if cat.get('display')]
                data['categories'] = '; '.join(category_names)
            except Exception:
                pass
    
    return data


def parse_all_pages(base_url):
    """
    Parse all HTML files in the pages directory and create a CSV file.
    """
    pages_dir = 'pages'
    output_csv = 'exhibitors_2026.csv'
    
    if not os.path.exists(pages_dir):
        print(f"Error: {pages_dir} directory not found!")
        return
    
    # Get all HTML files in the pages directory
    html_files = [f for f in os.listdir(pages_dir) if f.endswith('.html')]
    
    print(f"Found {len(html_files)} HTML files to parse...")
    
    # Prepare CSV
    fieldnames = [
        'url',
        'exhibitor_id',
        'company_name',
        'booth_number',
        'booth_url',
        'logo_url',
        'description',
        'address',
        'city',
        'state',
        'zip_code',
        'country',
        'website',
        'phone',
        'fax',
        'email',
        'facebook',
        'twitter',
        'instagram',
        'linkedin',
        'youtube',
        'categories',
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
                data = extract_exhibitor_data(html_content, exhibitor_id, base_url)
                
                # Write to CSV
                writer.writerow(data)
                
                if i % 50 == 0:
                    print(f"[{i}/{len(html_files)}] Parsed {data['company_name'] or exhibitor_id}")
                
            except Exception as e:
                print(f"Error parsing {filename}: {str(e)}")
                continue
    
    print(f"\nParsing complete! Data saved to {output_csv}")
    print(f"Total records: {len(html_files)}")


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] == "-h":
        print(HELP_TEXT)
        sys.exit(0)
    
    base_url = sys.argv[1].rstrip('/')
    parse_all_pages(base_url)
