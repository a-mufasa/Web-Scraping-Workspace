# Gets v8 vendors from a list of all vendors
from bs4 import BeautifulSoup
import sys

HELP_TEXT='''VENDORS GETTER!
Inputs an html file with just the <tbody> of the list of vendors in list view!

USAGE: python3 getVendors.py [html file]

ARGUMENTS
- html_file: The html file where the <tbody> is stored

Outputs a txt file with the same name as input but with .txt extension
'''

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == '-h':
        print(HELP_TEXT)
    else:
        with open(sys.argv[1], 'r') as f:
            data = f.read()

        soup = BeautifulSoup(data, 'html.parser')
        # THIS IS FOR LIST VIEW - find exhibitor detail links
        eles = soup.find_all('a', href=lambda href: href and 'exhibitor-details.cfm?exhid=' in href)

        exhids = []
        print(f'{len(eles)} listings found.')
        for ele in eles:
            exhid = ele.attrs['href'].split('exhid=')[-1].split('&')[0]
            if exhid not in exhids:  # Only add unique IDs
                exhids.append(exhid)

        with open(sys.argv[1].replace('.html', '.txt'), 'w') as f:
            f.write('\n'.join(exhids))