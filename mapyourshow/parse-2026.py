"""
parse-2026.py — SSE26 / mapyourshow 8.0 Vue.js page parser

SSE26 pages render contact info, social links, and description via inline
Vue component data() blocks rather than static HTML.  This parser targets
those script blocks with regex and falls back to <meta> tags where possible.

USAGE:
    uv run python mapyourshow/parse-2026.py https://sse26.mapyourshow.com [pages_dir] [output_csv]

    pages_dir   — folder of scraped .html files (default: pages/)
    output_csv  — output file path           (default: data-2026.csv)
"""

import sys
import os
import re
import json
import csv
from bs4 import BeautifulSoup

HELP_TEXT = __doc__

BASE_URL = None   # set from argv

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

def _str_val(text, key):
    """Extract  key: "value"  from a JS object literal (handles escaped chars)."""
    m = re.search(
        r'\b' + re.escape(key) + r':\s*"((?:[^"\\]|\\.)*)"',
        text
    )
    if not m:
        return ''
    return (
        m.group(1)
        .replace('\\"', '"')
        .replace('\\n', '\n')
        .replace('\\/', '/')   # JSON-escaped forward slashes (e.g. http:\/\/...)
        .strip()
    )


def _bool_val(text, key):
    m = re.search(r'\b' + re.escape(key) + r':\s*(true|false)\b', text)
    return m.group(1) == 'true' if m else False


def _addr_obj(text):
    """Extract addressValues: { ... } as a dict."""
    m = re.search(r'\baddressValues:\s*(\{[^}]*\})', text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


def _categories(text):
    """
    SSE26 pages no longer use `var productcategories`.
    Try to find a categoryList or productCategories array in any script block.
    Returns a list of category name strings (may be empty).
    """
    # Try JSON array of objects with a "NAME" or "name" key
    m = re.search(
        r'(?:categoryList|productCategories|productcategories)\s*[=:]\s*(\[[^\]]*\])',
        text, re.DOTALL | re.IGNORECASE
    )
    if m:
        try:
            cats = json.loads(m.group(1))
            names = []
            for c in cats:
                if isinstance(c, dict):
                    names.append(c.get('NAME') or c.get('name') or c.get('CATEGORYNAME') or '')
                elif isinstance(c, str):
                    names.append(c)
            return [n for n in names if n]
        except Exception:
            pass
    return []


# ---------------------------------------------------------------------------
# Per-page parser
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, html, exhid, base_url):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.exhid = exhid
        self.base_url = base_url.rstrip('/')
        # Concatenate all inline script text for regex searches
        self.scripts = '\n'.join(
            s.get_text() for s in self.soup.find_all('script') if s.get_text()
        )

    # ------------------------------------------------------------------
    # Static HTML fields (unchanged from previous years)
    # ------------------------------------------------------------------

    def originalUrl(self):
        return f'{self.base_url}/8_0/exhibitor/exhibitor-details.cfm?exhid={self.exhid}'

    def name(self):
        h1 = self.soup.find('h1', class_='exhibitor-name')
        if h1:
            return h1.get_text(strip=True)
        # fallback: og:title  (strips "2026 Sweets & Snacks Expo | " prefix)
        og = self.soup.find('meta', property='og:title')
        if og and og.get('content'):
            parts = og['content'].split('|', 1)
            return parts[-1].strip()
        return ''

    def logoUrl(self):
        img = self.soup.find('img', id='jq-exh-logo')
        if img and img.get('src'):
            src = img['src']
            if src.startswith('/'):
                return self.base_url + src
            return src
        return ''

    def booth(self):
        """Return booth text from the anchor (e.g. 'Exhibit Hall — 5225')."""
        a = self.soup.find('a', id=re.compile(r'^newfloorplanlink'))
        if a:
            # a.string works where get_text() fails on these pages
            if a.string:
                return str(a.string).strip()
            # fallback: extract booth number from URL param
            href = a.get('href', '')
            m = re.search(r'booth=(\w+)', href)
            if m:
                return m.group(1)
        return ''

    def boothUrl(self):
        a = self.soup.find('a', id=re.compile(r'^newfloorplanlink'))
        if a and a.get('href'):
            href = a['href']
            if href.startswith('/'):
                return self.base_url + href
            return href
        return ''

    # ------------------------------------------------------------------
    # Vue component data() fields
    # ------------------------------------------------------------------

    def website(self):
        return _str_val(self.scripts, 'websiteValue')

    def phone(self):
        return _str_val(self.scripts, 'phoneValue')

    def fax(self):
        return _str_val(self.scripts, 'faxValue')

    def address(self):
        addr = _addr_obj(self.scripts)
        if not addr:
            return ''
        parts = [
            addr.get('ADDRESS1', ''),
            addr.get('ADDRESS2', ''),
            addr.get('ADDRESS3', ''),
            addr.get('CITY', ''),
            addr.get('STATE', ''),
            addr.get('ZIP', ''),
            addr.get('COUNTRY', ''),
        ]
        return ', '.join(p for p in parts if p)

    def facebook(self):
        return _str_val(self.scripts, 'facebookValue')

    def twitter(self):
        return _str_val(self.scripts, 'twitterValue')

    def instagram(self):
        return _str_val(self.scripts, 'instagramValue')

    def linkedin(self):
        return _str_val(self.scripts, 'linkedInValue')

    def description(self):
        # Target the sectionDescription Vue component data block
        m = re.search(
            r"sectionDescription\s*=\s*Vue\.component.*?description:\s*\"((?:[^\"\\]|\\.)*?)\"",
            self.scripts, re.DOTALL
        )
        if m:
            return m.group(1).replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/').strip()
        # Fallback: meta description tag
        meta = self.soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        return ''

    def categories(self):
        cats = _categories(self.scripts)
        return ' | '.join(cats)

    # ------------------------------------------------------------------
    # Build output dict
    # ------------------------------------------------------------------

    def parse(self):
        return {
            'originalUrl':   self.originalUrl(),
            'name':          self.name(),
            'logoUrl':       self.logoUrl(),
            'booth':         self.booth(),
            'boothUrl':      self.boothUrl(),
            'address':       self.address(),
            'website':       self.website(),
            'phone':         self.phone(),
            'fax':           self.fax(),
            'facebook':      self.facebook(),
            'twitter':       self.twitter(),
            'instagram':     self.instagram(),
            'linkedin':      self.linkedin(),
            'description':   self.description(),
            'categories':    self.categories(),
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(HELP_TEXT)
        sys.exit(0)

    base_url = sys.argv[1].rstrip('/')
    pages_dir = sys.argv[2] if len(sys.argv) > 2 else 'pages/'
    output_csv = sys.argv[3] if len(sys.argv) > 3 else 'data-2026.csv'

    if not pages_dir.endswith('/'):
        pages_dir += '/'

    files = [f for f in os.listdir(pages_dir) if f.endswith('.html')]
    total = len(files)
    print(f'Parsing {total} pages from {pages_dir} ...')

    FIELDS = [
        'originalUrl', 'name', 'logoUrl', 'booth', 'boothUrl',
        'address', 'website', 'phone', 'fax',
        'facebook', 'twitter', 'instagram', 'linkedin',
        'description', 'categories',
    ]

    results = []
    errors = []

    for i, fname in enumerate(sorted(files), 1):
        exhid = fname.replace('_SLASH_', '/').replace('.html', '')
        path = pages_dir + fname
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
            p = Parser(html, exhid, base_url)
            results.append(p.parse())
        except Exception as e:
            errors.append((fname, str(e)))

        if i % 100 == 0 or i == total:
            print(f'  {i}/{total}')

    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f'\nWrote {len(results)} rows to {output_csv}')
    if errors:
        print(f'{len(errors)} errors:')
        for fname, err in errors:
            print(f'  {fname}: {err}')
