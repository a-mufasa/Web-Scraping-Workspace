# Parse v8 mapyourshow pages; Of course, each mapyourshow conference is different, so may require some tweaking
import json
import os
import sys
import re
from bs4 import BeautifulSoup

HELP_TEXT='''Parser! Parse mapyourshow.com pages
USAGE: python3 parse.py [base_url]

ARGUMENTS
- base_url: The host of the site. EX: https://wff2024.mapyourshow.com

It reads pages from the pages/ dir, and outputs to data.json
'''

class Parser:
    def __init__(self, data: str, page_id: str):
        self.soup = BeautifulSoup(data, 'html')
        self.base_url = sys.argv[1].rstrip('/')
        self.url = self.base_url + '/8_0/exhibitor/exhibitor-details.cfm?exhid=' +\
            page_id.replace('.html', '')

    def muted(self, string: str) -> str:
        return self.soup.find('span', class_='muted', string=string) or None

    def parse(self) -> dict:
        comp = {
            'originalUrl': self.url
        }

        if name:= self.soup.find('h1', attrs={'class': re.compile('^mr3-m')}):
            comp['name'] = name.text.strip().replace('\u2013', '')
        
        if logo := self.soup.find('img', id='jq-exh-logo'):
            comp['logoUrl'] = self.base_url + logo.attrs['src'].strip()

        if booth := self.soup.find('a', id='newfloorplanlink'):
            comp['booth'] = booth.text.replace('\u2014', '-')
            comp['boothUrl'] = self.base_url + booth.attrs['href']
        
        if address := self.soup.find('p', attrs={'class': re.compile('^showcase-address')}):
            comp['address'] = address.get_text(strip=True).replace('\n\t\t\t\t\t\t', ' ')

        if website := self.soup.find('a', attrs={'title': 'Visit our website'}):
            comp['website'] = website.attrs['href']
        
        if phone := self.muted('Phone:'):  
            phone = phone.parent
            for span in phone.find_all('span'):
                span.extract() 
            comp['phone'] = phone.get_text(strip=True)

        social_template = r'http(s|):\/\/(www\.|.*\.){}\/.*'
        socialMedias = {
            'facebook': re.compile(social_template.format('facebook.com')),
            'twitter': re.compile(social_template.format('twitter.com')),
            'instagram': re.compile(social_template.format('instagram.com')),
            'linkedin': re.compile(social_template.format('linkedin.com'))
        }

        for soc, reg in socialMedias.items():
            if soc_url := self.soup.find('a', attrs={'href': reg}):
                comp[soc] = soc_url.attrs['href'].strip()

        
        if description := self.soup.find('p', attrs={'class': 'js-read-more'}):
            comp['description'] = description.get_text(strip=True).replace('\u00a9', '').replace('\u2019', "'").replace('\n', '')\
                .replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', "-").replace('\u2014',"-")

        if categories := self.soup.find('script', string=re.compile('var productcategories')):
            cat_match = re.search(r"productcategories:\n\s+(\[.+?\])", categories.text, re.MULTILINE | re.DOTALL)
            categories = cat_match[0].replace('\t', '').replace('\n','').replace(',}', '}').replace("'", '"').replace('productcategories:', '')
            cat_dicts = json.loads(categories)

            for d in cat_dicts:
                del d['url']

            comp['categories'] = cat_dicts
        
        return comp

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == '-h':
        print(HELP_TEXT)
    else:
        pages = os.listdir('pages/')
        companies = []

        page_len = len(pages)
        
        for counter, page in enumerate(pages):
            try:
                with open(f'pages/{page}', 'r') as f:
                    page_data = f.read()
                companies.append(Parser(page_data, page).parse())
            except Exception as e:
                print(f'Error rose from {page}')
                raise e
                
            if counter % 50 == 0:
                print(f'Completed {counter} of {page_len}')

        with open('data.json', 'w') as f:
            json.dump(companies, f)
   