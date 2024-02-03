import os
import re
import sys
import json
import urllib
from bs4 import BeautifulSoup

class Parser:
    def __init__(self, filename: str, base_url: str):
        self.filename = filename
        self.base_url = base_url.rstrip('/')
        self.help_text = f'''Expo West Parser! Parse Expo West links
        USAGE: python3 {filename}

        ARGUMENTS
        - base_url: The base_url of the site, up to whatever the page_id is EX: "https://example.com/page/"
        - input_dir (optional): Defaults to pages/, but if provided, will use that folder

        It reads pages from the pages/ dir (default), and outputs to data.json
        '''

    def remove_mega_spaces(self, text: str, newlines=True) -> str:
        if newlines:
            text = re.split(r' |\n|\t|\u00a0|\u202f|\ufffd|\u200b', text)
        else:
            text = re.split(r' |\t|\u00a0|\u202f|\ufffd|\u200b', text)
        text = list(filter(None, text))
        return ' '.join(text).strip()

    def parse_socials(self, soup) -> dict:
        socials = {}
        social_template = r'http(s|):\/\/(www\.|.*\.){}\/.*'
        social_medias = {
            'facebook': re.compile(social_template.format('facebook.com')),
            'twitter': re.compile(social_template.format('twitter.com')),
            'instagram': re.compile(social_template.format('instagram.com')),
            'linkedin': re.compile(social_template.format('linkedin.com')),
            'youtube': re.compile(social_template.format('youtube.com')),
        }

        for soc, reg in social_medias.items():
            if soc_url := soup.find('a', attrs={'href': reg}):
                socials[soc] = soc_url.attrs['href'].strip()
            elif soc_url := soup.find('a', attrs={'data-href': reg}):
                socials[soc] = soc_url.attrs['data-href'].strip()

        return socials

    def parse(self, data: str, page_id: str) -> dict:
        comp = {
            'originalUrl': self.join_url(self.base_url, page_id.replace('_SLASH_', '/').replace('.html', ''))
        }

        soup = BeautifulSoup(data, 'html')
        footer = soup.find('div', id='footer-container')
        if footer:
            footer.extract()

        if name := soup.find('h2', class_='content-title'):
            comp['name'] = name.text.strip()

        if website := soup.find('a', class_='pes-external-link-gate'):
            comp['website'] = website.attrs['data-href']

        if address := soup.find('li', class_='BoothContactCountry'):
            comp['address'] = self.remove_mega_spaces(address.parent.text)

        comp.update(self.parse_socials(soup))

        if description := soup.find('p', class_='BoothPrintProfile'):
            comp['description'] = self.remove_mega_spaces(description.text)

        if categories := soup.find_all('div', class_='ProductCategoryContainer'):
            comp['categories'] = [{'name': cat.find('strong').text,
                                   'subcategories': [li.text.strip() for li in cat.find_all('li', class_='ProductCategoryLi')]}
                                  for cat in categories]

        if brands := soup.find('p', class_='BoothBrands'):
            b_tag = brands.find('b')
            if b_tag:
                b_tag.extract()
            comp['brands'] = self.remove_mega_spaces(brands.text)

        return comp

    @staticmethod
    def join_url(url1: str, url2: str) -> str:
        return urllib.parse.urljoin(url1, url2)

    def get(self):
        if len(sys.argv) < 2 or sys.argv[1] == '-h':
            print(self.help_text)
        else:
            pages_dir = 'pages/' if len(sys.argv) < 3 else sys.argv[2]
            pages = os.listdir(pages_dir)
            try:
                pages.remove('.DS_Store')
            except ValueError:
                pass
            companies = []

            for page in pages:
                with open(os.path.join(pages_dir, page), 'r') as f:
                    page_data = f.read()
                companies.append(self.parse(page_data, page))

            with open('data.json', 'w') as f:
                json.dump(companies, f, indent=4)

if __name__ == "__main__":
    base_url = "https://example.com"  # Adjust as necessary
    parser = Parser('parsew.py', base_url)
    parser.get()
