import json
import os
import sys
import re
from bs4 import BeautifulSoup

HELP_TEXT = '''Parser! Parse mapyourshow.com pages
USAGE: python3 parse.py [base_url]

ARGUMENTS:
- base_url: The host of the site. EX: https://wff2024.mapyourshow.com

It reads pages from the pages/ dir, and outputs to data.json
'''

class Parser:
    def __init__(self, data: str, page_id: str):
        # Explicitly set the parser to "html.parser" to avoid parser warnings.
        self.soup = BeautifulSoup(data, features="html.parser")
        self.base_url = sys.argv[1].rstrip('/')
        self.page_id = page_id
        self.url = f"{self.base_url}/8_0/exhibitor/exhibitor-details.cfm?exhid={page_id.replace('.html', '')}"
    
    def muted(self, string: str):
        # Finds a <span class="muted"> with the exact text,
        # ensuring it is not inside a <script> tag.
        element = self.soup.find('span', class_='muted', string=string)
        if element and element.find_parent('script'):
            return None
        return element

    def parse(self) -> dict:
        comp = {"originalUrl": self.url}

        # NAME
        name_tag = self.soup.find('h1', class_=re.compile(r'(exhibitor[-_\s]?name|mr3-m)', re.I))
        if name_tag and name_tag.get_text(strip=True):
            comp["name"] = name_tag.get_text(strip=True)
        else:
            meta_title = self.soup.find('meta', property='og:title')
            if meta_title and meta_title.get("content"):
                comp["name"] = meta_title["content"].split(" - ")[0].strip()

        # LOGO
        logo_tag = self.soup.find('img', id=re.compile(r'logo', re.I)) or \
                   self.soup.find('img', class_=re.compile(r'logo', re.I))
        if logo_tag and logo_tag.get("src"):
            src = logo_tag["src"].strip()
            comp["logoUrl"] = self.base_url + src if src.startswith("/") else src

        # BOOTH: Look for the anchor with id "newfloorplanlink"
        booth_tag = self.soup.find('a', id="newfloorplanlink")
        if booth_tag:
            # Try to get text using get_text with a separator; if that fails, use decode_contents()
            booth_text = booth_tag.get_text(separator=" ", strip=True)
            if not booth_text:
                booth_text = booth_tag.decode_contents().strip()
            comp["booth"] = booth_text.replace("\u2014", "-")
            href = booth_tag.get("href")
            if href:
                comp["boothUrl"] = self.base_url + href if href.startswith("/") else href
        else:
            # Fallback: search for any anchor whose id contains "floorplan"
            booth_tag = self.soup.find('a', id=re.compile(r'floorplan', re.I))
            if booth_tag:
                booth_text = booth_tag.get_text(separator=" ", strip=True)
                if not booth_text:
                    booth_text = booth_tag.decode_contents().strip()
                comp["booth"] = booth_text.replace("\u2014", "-")
                href = booth_tag.get("href")
                if href:
                    comp["boothUrl"] = self.base_url + href if href.startswith("/") else href

        # ADDRESS: look for a <p> with a class containing "showcase-address"
        address_tag = self.soup.find('p', class_=re.compile(r'showcase-address', re.I))
        if address_tag:
            comp["address"] = address_tag.get_text(separator=' ', strip=True)
        
        # WEBSITE: find an anchor with title "Visit our website"
        website_tag = self.soup.find('a', title=re.compile(r'Visit our website', re.I))
        if website_tag and website_tag.get("href"):
            comp["website"] = website_tag["href"].strip()

        # PHONE: first try an anchor with href starting with "tel:"
        tel_tag = self.soup.find('a', href=re.compile(r'^tel:', re.I))
        if tel_tag:
            comp["phone"] = tel_tag.get_text(strip=True)
        else:
            phone_element = self.muted("Phone:")
            if phone_element:
                parent = phone_element.parent
                for span in parent.find_all("span"):
                    span.decompose()
                extracted = parent.get_text(strip=True).replace("Phone:", "").strip()
                if re.search(r'\d', extracted):
                    comp["phone"] = extracted

        # SOCIAL MEDIA
        social_template = r'^https?://(?:www\.)?{}[/\w-]*'
        social_medias = {
            "facebook": re.compile(social_template.format("facebook\\.com"), re.I),
            "twitter": re.compile(social_template.format("twitter\\.com"), re.I),
            "instagram": re.compile(social_template.format("instagram\\.com"), re.I),
            "linkedin": re.compile(social_template.format("linkedin\\.com"), re.I)
        }
        for key, pattern in social_medias.items():
            tag = self.soup.find("a", href=pattern)
            if tag and tag.get("href"):
                comp[key] = tag["href"].strip()

        # DESCRIPTION: look for a <p> or <div> with a class suggesting a description.
        desc_tag = self.soup.find(lambda tag: tag.name in ["p", "div"] and tag.get("class") and 
                                    any(re.search(r"(description|read[-]?more)", cls, re.I) for cls in tag.get("class")))
        if desc_tag:
            comp["description"] = desc_tag.get_text(separator=" ", strip=True) \
                .replace("\u00a9", "").replace("\u2019", "'") \
                .replace("\n", "").replace("\u201c", '"').replace("\u201d", '"') \
                .replace("\u2013", "-").replace("\u2014", "-")
        
        # CATEGORIES: look in a script tag for a JSON array in "productcategories"
        script_tag = self.soup.find("script", string=re.compile(r"productcategories"))
        if script_tag and script_tag.string:
            cat_match = re.search(r"productcategories:\s*(\[[^\]]+\])", script_tag.string, re.MULTILINE | re.DOTALL)
            if cat_match:
                try:
                    categories = json.loads(cat_match.group(1).replace("'", '"'))
                    for cat in categories:
                        cat.pop("url", None)
                    comp["categories"] = categories
                except Exception:
                    comp["categories"] = []
        return comp

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == "-h":
        print(HELP_TEXT)
        sys.exit(0)
    pages = os.listdir("pages/")
    companies = []
    total_pages = len(pages)
    for i, page in enumerate(pages):
        try:
            with open(f"pages/{page}", "r") as f:
                data = f.read()
            companies.append(Parser(data, page).parse())
        except Exception as e:
            print(f"Error processing {page}: {e}")
        if i % 50 == 0:
            print(f"Processed {i} of {total_pages}")
    with open("data.json", "w") as f:
        json.dump(companies, f, indent=2)
