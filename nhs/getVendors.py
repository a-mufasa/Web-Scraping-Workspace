import re
import sys
from urllib.parse import unquote

from bs4 import BeautifulSoup

HELP_TEXT = """NHS Vendor Extractor
Extracts organisation IDs from copied exhibitor list HTML.

USAGE: python3 getVendors.py [vendors_html (optional)] [output_file (optional)]

- vendors_html (optional) = HTML file copied from the exhibitor list page; defaults to vendors.html
- output_file (optional) = output txt file; defaults to vendors.txt
"""


ORG_ID_PATTERN = re.compile(r"\.org-([0-9a-fA-F-]{36})\.html")


def extract_org_ids(html_content):
    """Extract unique organisation IDs from exhibitor detail links."""
    soup = BeautifulSoup(html_content, "html.parser")

    org_ids = []
    seen = set()

    links = soup.find_all("a", href=True)
    for link in links:
        href_value = link.get("href")
        if not isinstance(href_value, str):
            continue

        href = unquote(href_value)
        if "exhibitor-details" not in href:
            continue

        match = ORG_ID_PATTERN.search(href)
        if not match:
            continue

        org_id = f"org-{match.group(1).lower()}"
        if org_id not in seen:
            seen.add(org_id)
            org_ids.append(org_id)

    return org_ids


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print(HELP_TEXT)
        return

    input_file = sys.argv[1] if len(sys.argv) > 1 else "vendors.html"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "vendors.txt"

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return

    org_ids = extract_org_ids(html_content)

    if not org_ids:
        print(
            "No organisation IDs found. Make sure vendors HTML contains exhibitor detail links."
        )
        return

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(org_ids))

    print(f"Found {len(org_ids)} unique organisations")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
