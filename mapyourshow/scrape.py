import sys
import os
import httpx
import asyncio
import random

HELP_TEXT = '''Scraper! Scrapes lists of pages (concurrent async + retry)
USAGE python3 scrape.py [list to exhids] [base_url] [output (optional)] [concurrency (optional)]

- list to exhids  = .txt file with list of exhibition ids (one per line)
- base_url        = URL prefix before the exhid
                    EX: https://sse26.mapyourshow.com/8_0/exhibitor/exhibitor-details.cfm?exhid=
- output          = folder to store pages in (default: pages/)
- concurrency     = number of parallel requests (default: 10)
'''

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://sse26.mapyourshow.com/8_0/explore/exhibitor-alphalist.cfm',
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

MAX_RETRIES = 4


async def fetch(client, sem, base_url, exhid, output_path, errors):
    name = exhid.replace('/', '_SLASH_')
    path = f'{output_path}{name}.html'
    if os.path.exists(path):
        return

    async with sem:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = await client.get(base_url + exhid, timeout=20)
                if r.status_code == 200:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(r.text)
                    return
                else:
                    err = f'HTTP {r.status_code}'
            except Exception as e:
                err = str(e)

            if attempt < MAX_RETRIES:
                wait = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait)
            else:
                errors.append((exhid, err))
                print(f'  FAIL {exhid}: {err}')


async def main(ids, base_url, output_path, concurrency):
    os.makedirs(output_path, exist_ok=True)

    total = len(ids)
    already = sum(1 for i in ids if os.path.exists(f'{output_path}{i.replace("/", "_SLASH_")}.html'))
    to_fetch = total - already
    print(f'{total} IDs total, {already} already downloaded, {to_fetch} to fetch (concurrency={concurrency})')

    if to_fetch == 0:
        print('Nothing to do.')
        return

    sem = asyncio.Semaphore(concurrency)
    errors = []
    done = 0

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        tasks = [
            fetch(client, sem, base_url, exhid, output_path, errors)
            for exhid in ids
        ]

        for coro in asyncio.as_completed(tasks):
            await coro
            done += 1
            if done % 50 == 0 or done == total:
                downloaded = sum(1 for i in ids if os.path.exists(f'{output_path}{i.replace("/", "_SLASH_")}.html'))
                print(f'  {done}/{total} tasks — {downloaded} files on disk')

    print(f'\nDone. {len(errors)} permanent errors.')
    for exhid, err in errors:
        print(f'  {exhid}: {err}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(HELP_TEXT)
        sys.exit(0)

    with open(sys.argv[1], 'r') as f:
        ids = [line.strip() for line in f if line.strip()]

    base_url = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else 'pages/'
    if not output_path.endswith('/'):
        output_path += '/'
    concurrency = int(sys.argv[4]) if len(sys.argv) > 4 else 10

    asyncio.run(main(ids, base_url, output_path, concurrency))
