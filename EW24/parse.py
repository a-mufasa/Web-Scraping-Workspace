import json
import os
import sys
import re
from bs4 import BeautifulSoup

HELP_TEXT = '''Parser! Parse smallworldlabs.com pages
USAGE: python3 parse.py [base_url]

ARGUMENTS
- base_url: The host of the site. EX: https://expowest24.smallworldlabs.com

It reads pages from the pages/ dir, and outputs to data.json
'''

class Parser:
    def __init__(self, data: str, page_id: str):
        self.soup = BeautifulSoup(data, 'html.parser')
        self.base_url = sys.argv[1].rstrip('/')
        self.url = self.base_url + '/?page_id=2424&boothId=' + page_id.replace('.html', '')

    def parse_address(self, address_marker):
        if address_marker:
            # Use .decode_contents() to retain HTML entities like new lines
            address_html = address_marker.decode_contents()
            # Replace <br/> tags with a space to ensure proper spacing in the address
            address_html = address_html.replace('<br/>', ' ').replace('<br>', ' ')
            # Now parse this modified HTML to extract clean text
            clean_address = BeautifulSoup(address_html, 'html.parser').get_text(' ', strip=True)
            return clean_address
        return ""

    def parse(self) -> dict:
        comp = {'originalUrl': self.url}

        # Extract Booth Number
        booth_marker = self.soup.find('a', href=lambda href: href and 'eventmap.aspx' in href)
        if booth_marker:
            comp['booth'] = booth_marker.get_text(strip=True)

        # Extracting Sections from About Tab
        about_marker = self.soup.find('div', id=lambda id: id and id.endswith('_about'))
        if about_marker:
            for item in about_marker.find_all('div', class_='row'):
                key = item.find('div', class_='text-secondary').get_text(strip=True).replace(' ', '_')
                value = item.find('div', class_='profileResponse').get_text(strip=True)
                comp[key] = value

        # Extracting Contact Info
        contact_marker = self.soup.find('div', id=lambda id: id and id.endswith('_contact'))
        if contact_marker:
            for item in contact_marker.find_all('div', class_='row'):
                key = item.find('div', class_='text-secondary').get_text(strip=True)
                value = item.find('div', class_='profileResponse')
                if key == "Address":
                    value = self.parse_address(value)
                else:
                    value = value.get_text(strip=True)
                comp[key] = value

        # Extracting Additional Info
        additional_info_marker = self.soup.find('div', id=lambda id: id and id.endswith('_custom'))
        if additional_info_marker:
            for item in additional_info_marker.find_all('div', class_='row'):
                key = item.find('div', class_='text-secondary').get_text(strip=True).replace(' ', '_')
                value = item.find('div', class_='profileResponse').get_text(strip=True)
                comp[key] = value

        # Extracting Organization Member List
        member_list_marker = self.soup.find('div', class_='generic-list-wrapper')
        if member_list_marker:
            members = [member.get_text(strip=True) for member in member_list_marker.find_all('h6')]
            comp['org_members'] = members

        return comp

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == '-h':
        print(HELP_TEXT)
    else:
        pages = os.listdir('pages/')
        companies = []

        for counter, page in enumerate(pages):
            try:
                with open(f'pages/{page}', 'r') as f:
                    page_data = f.read()
                parsed_data = Parser(page_data, page).parse()
                companies.append(parsed_data)
            except Exception as e:
                print(f'Error rose from {page}: {str(e)}')

            if counter % 50 == 0:
                print(f'Completed {counter} of {len(pages)}')

        with open('data.json', 'w') as f:
            json.dump(companies, f, ensure_ascii=False, indent=4)
