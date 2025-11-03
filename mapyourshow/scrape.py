import sys
import os
import httpx
import time

HELP_TEXT = '''Scraper! Scrapes lists of pages
USAGE python3 scrape.py [list to exhids] [base_url] [output (optional)]

- list to exhids = Literally a .txt file with list of exhibition ids
- base_url = All the url before the exhid. EX: https://wff2025.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid=
- output (optional) = the name of the folder to store in; Default to pages
'''

if len(sys.argv) < 3:
    print(HELP_TEXT)
else:
    client = httpx.Client()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://wff2025.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    cookies = {
        'CFID': '51997898',
        'CFTOKEN': '3585f8544522eca6-CA55A7C2-C172-DE01-73DE70718AC2B5DF',
        'JSESSIONID': '268F88B625E2BBD8DBEE2F7C5196D0A5.vts',
    }

    client.headers.update(headers)
    client.cookies.update(cookies)

    base_url = sys.argv[2]
    with open(sys.argv[1], 'r') as f:
        urls = f.read()

    try:
        output = sys.argv[3]
        if not output.endswith('/'):
            output += '/'
    except IndexError:
        output = 'pages/'

    if not os.path.exists(output):
        os.makedirs(output)

    urls = urls.split('\n')

    urls_len = len(urls)

    for counter, url in enumerate(urls):
        name = url.replace('/', '_SLASH_')
        output_path = f'{output}{name}.html'
        if not os.path.exists(output_path):
            try:
                response = client.get(base_url + url, timeout=10)
                if response.status_code == 200:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                else:
                    print(f"Failed to fetch {base_url + url}: HTTP {response.status_code}")
            except httpx.RequestError as e:
                print(f"Error fetching {base_url + url}: {e}")

        if counter % 25 == 0:
            print(f'Completed {counter} out of {urls_len} pages')

        # Throttle requests
        time.sleep(1)  # Delay to avoid rate-limiting
