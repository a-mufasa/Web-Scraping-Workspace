from bs4 import BeautifulSoup
import sys

HELP_TEXT = '''Expo West Vendors Getter
Input an html file with just the <tbody> of the list of vendors.

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

        eles = soup.find_all('a', class_='exhibitorName')

        print(f'{len(eles)} listings found.')

        # Extract just the numeric ID after "BoothID=", excluding any trailing parameters
        booth_ids = [ele.attrs['href'].split('BoothID=')[-1].split('&')[0] for ele in eles if 'BoothID=' in ele.attrs['href']]

        with open(sys.argv[1].replace('.html', '.txt'), 'w') as f:
            f.write('\n'.join(booth_ids))
