from bs4 import BeautifulSoup
import re

# Read the vendors HTML file
with open('vendors.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all exhibitor links using regex pattern
# Pattern: href="/event/winter-fancyfaire/exhibitor/[exhibitor_id]"
exhibitor_links = soup.find_all('a', href=re.compile(r'/event/winter-fancyfaire/exhibitor/'))

# Extract unique exhibitor IDs
exhibitor_ids = set()
for link in exhibitor_links:
    href = link.get('href')
    # Extract the exhibitor ID from the URL
    # Format: /event/winter-fancyfaire/exhibitor/RXhoaWJpdG9yXzIyOTA4MjE=
    match = re.search(r'/exhibitor/([^/]+)$', href)
    if match:
        exhibitor_id = match.group(1)
        exhibitor_ids.add(exhibitor_id)

# Write the exhibitor IDs to a file
with open('exhibitor_ids.txt', 'w', encoding='utf-8') as f:
    for exhibitor_id in sorted(exhibitor_ids):
        f.write(f"{exhibitor_id}\n")

print(f"Found {len(exhibitor_ids)} unique exhibitors")
print(f"Exhibitor IDs saved to exhibitor_ids.txt")
