from bs4 import BeautifulSoup
import sys

HELP_TEXT = '''National Hardware Show Vendors Getter
Input an html file with just the <ul> of the list of vendors.

USAGE: python3 getVendors.py [html file]

ARGUMENTS
- html_file: The html file where the <ul> is stored

Outputs a txt file with the same name as input but with .txt extension
'''

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == '-h':
        print(HELP_TEXT)
    else:
        with open(sys.argv[1], 'r') as f:
            data = f.read()

        soup = BeautifulSoup(data, 'html.parser')

        exhibitor_containers = soup.find_all('div', class_='directory-item')
        
        prefix = "https://www.nationalhardwareshow.com/en-us/attend/exhibitor-list/exhibitor-details."
        hrefs = []

        for container in exhibitor_containers:
            first_a = container.find('a', href=True)
            if first_a and first_a['href'].startswith(prefix):
                href_part = first_a['href'][len(prefix):]
                hrefs.append(href_part)

        print(f'{len(hrefs)} listings found.')

        with open(sys.argv[1].replace('.html', '.txt'), 'w') as f:
            f.write('\n'.join(hrefs))