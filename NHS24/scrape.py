import sys
import os
import requests

HELP_TEXT = '''Scraper! Scrapes lists of pages
USAGE python3 scrape.py [list to exhids] [base_url] [output (optional)]

- list to exhids = Literally a .txt file with list of exhibition ids
- base_url = All the url before the exhid. EX: https://expowest24.smallworldlabs.com/?page_id=2424&boothId=
- output (optional) = the name of the folder to store in; Default to pages
'''

if len(sys.argv) < 3:
    print(HELP_TEXT)
else:
    s = requests.session()
    base_url = sys.argv[2]
    with open(sys.argv[1], 'r') as f:
        urls = f.read()

    try:
        output = sys.argv[3]
        if not output.endswith('/'):
            output += '/'
    except IndexError:
        output = 'pages/'

    urls = urls.split('\n')

    urls_len = len(urls)

    for counter, url in enumerate(urls):
        name = url.replace('/', '_SLASH_')
        if not os.path.exists(f'{output}{name}.html'):
            txt = s.get(base_url + url).text
            with open(f'{output}{name}.html', 'w') as f:
                f.write(txt)

        if counter % 25 == 0:
            print(f'Completed {counter} out of {urls_len} pages')