import sys
import json
import csv
from pathlib import Path

HELP_TEXT = """Parser! Extracts data from exhibitor JSON files
USAGE: uv run parse.py [pages_dir] [output_csv] [limit (optional)]

- pages_dir = directory containing downloaded JSON files (from scrape.py)
- output_csv = output CSV file name
- limit (optional) = number of files to parse for testing; Default = all files
"""


def sanitize_text(text):
    """Remove unusual line terminators and problematic characters"""
    if not text:
        return ""

    # Remove Line Separator (U+2028) and Paragraph Separator (U+2029)
    text = text.replace("\u2028", " ").replace("\u2029", " ")

    # Replace other problematic characters
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")

    # Normalize multiple spaces to single space
    text = " ".join(text.split())

    return text


def get_social_url(social_type, profile):
    """Convert social network type and profile to full URL"""
    if not profile:
        return ""

    # Remove @ prefix if present
    profile = profile.lstrip("@")

    social_urls = {
        "TWITTER": f"https://twitter.com/{profile}",
        "FACEBOOK": f"https://facebook.com/{profile}",
        "INSTAGRAM": f"https://instagram.com/{profile}",
        "LINKEDIN": f"https://linkedin.com/company/{profile}",
        "YOUTUBE": f"https://youtube.com/{profile}",
    }

    return social_urls.get(social_type, profile)


def extract_field_value(fields, field_name):
    """Extract value from fields array by field name"""
    if not fields:
        return ""

    for field in fields:
        if field.get("name") == field_name:
            if field.get("__typename") == "Core_SelectField":
                value = field.get("value")
                if value:
                    return value.get("text", "")
            elif field.get("__typename") == "Core_UrlField":
                value = field.get("value")
                if value:
                    return value.get("url", "")
            elif field.get("__typename") == "Core_TreeField":
                values = field.get("values", [])
                if values:
                    return ", ".join(
                        [v.get("text", "") for v in values if v.get("text")]
                    )
    return ""


def parse_exhibitor_json(json_file):
    """Parse a single exhibitor JSON file"""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {json_file}: {e}")
        return None

    try:
        # Extract exhibitor ID from filename
        exhibitor_id = json_file.stem  # filename without extension

        # Parse response structure
        if not json_data or len(json_data) == 0:
            return None

        response = json_data[0]
        if "data" not in response or "exhibitor" not in response["data"]:
            return None

        exhibitor = response["data"]["exhibitor"]

        # Handle None values with .get() and defaults
        with_event = exhibitor.get("withEvent") or {}
        fields = with_event.get("fields") or []
        address = exhibitor.get("address") or {}

        # Build exhibitor URL
        exhibitor_url = f"https://attend.expowest.com/widget/event/natural-products-expo-west-2026/exhibitor/{exhibitor_id}"

        # Extract basic info with safe defaults and sanitize text
        row = {
            "exhibitor_url": exhibitor_url,
            "name": sanitize_text(exhibitor.get("name") or ""),
            "type": sanitize_text(exhibitor.get("type") or ""),
            "website": exhibitor.get("websiteUrl") or "",
            "email": exhibitor.get("email") or "",
            "description": sanitize_text(exhibitor.get("description") or ""),
            "logo_url": exhibitor.get("logoUrl") or "",
        }

        # Extract address safely
        row["country"] = sanitize_text(address.get("country") or "")
        row["state"] = sanitize_text(address.get("state") or "")
        row["city"] = sanitize_text(address.get("city") or "")
        row["street"] = sanitize_text(address.get("street") or "")
        row["zip_code"] = address.get("zipCode") or ""

        # Extract booths
        booths = with_event.get("booths") or []
        row["booth_numbers"] = ", ".join(
            [b.get("name", "") for b in booths if b.get("name")]
        )

        # Extract custom fields and sanitize
        row["hall"] = sanitize_text(extract_field_value(fields, "Hall"))
        row["product_category"] = sanitize_text(
            extract_field_value(fields, "Product Category")
        )
        row["first_time_exhibitor"] = sanitize_text(
            extract_field_value(fields, "First Time Exhibitors")
        )
        row["fresh_ideas_organic"] = sanitize_text(
            extract_field_value(fields, "Fresh Ideas Organic Marketplace")
        )
        row["us_state_canadian_province"] = sanitize_text(
            extract_field_value(fields, "US State/Canadian Providence")
        )
        row["beacon_url"] = extract_field_value(
            fields, "Learn about this brand on Beacon Discovery"
        )

        # Extract social networks with full URLs
        social_networks = exhibitor.get("socialNetworks") or []
        row["twitter"] = ""
        row["facebook"] = ""
        row["instagram"] = ""
        row["linkedin"] = ""
        row["youtube"] = ""

        for social in social_networks:
            network_type = social.get("type", "").upper()
            profile = social.get("profile", "")
            if network_type and profile:
                full_url = get_social_url(network_type, profile)
                if network_type == "TWITTER":
                    row["twitter"] = full_url
                elif network_type == "FACEBOOK":
                    row["facebook"] = full_url
                elif network_type == "INSTAGRAM":
                    row["instagram"] = full_url
                elif network_type == "LINKEDIN":
                    row["linkedin"] = full_url
                elif network_type == "YOUTUBE":
                    row["youtube"] = full_url

        # Extract phone numbers
        phone_numbers = exhibitor.get("phoneNumbers") or []
        if phone_numbers:
            row["phone"] = ", ".join(
                [p.get("number", "") for p in phone_numbers if p.get("number")]
            )
        else:
            row["phone"] = ""

        # Count of team members
        members = response["data"].get("members") or {}
        row["team_members_count"] = members.get("totalCount", 0)

        return row

    except Exception as e:
        print(f"Error parsing {json_file}: {e}")
        return None


def parse_all(pages_dir, output_csv, limit=None):
    """Parse all JSON files and write to CSV"""
    pages_path = Path(pages_dir)

    if not pages_path.exists():
        print(f"Error: Directory {pages_dir} does not exist")
        return

    json_files = list(pages_path.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {pages_dir}")
        return

    # Limit number of files if specified
    if limit and limit > 0:
        json_files = json_files[:limit]
        print(f"Limited to {len(json_files)} files for testing\n")

    print(f"Found {len(json_files)} JSON files to parse\n")

    results = []

    for i, json_file in enumerate(json_files, 1):
        result = parse_exhibitor_json(json_file)

        if result:
            results.append(result)

        if i % 25 == 0 or i == len(json_files):
            print(f"Parsed {i} out of {len(json_files)} files")

    # Write to CSV
    if results:
        # Define fieldnames in desired order
        fieldnames = [
            "exhibitor_url",
            "name",
            "type",
            "website",
            "email",
            "phone",
            "description",
            "booth_numbers",
            "hall",
            "country",
            "state",
            "city",
            "street",
            "zip_code",
            "product_category",
            "first_time_exhibitor",
            "fresh_ideas_organic",
            "us_state_canadian_province",
            "twitter",
            "facebook",
            "instagram",
            "linkedin",
            "youtube",
            "logo_url",
            "beacon_url",
            "team_members_count",
        ]

        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()

            for result in results:
                # Ensure all fields exist with empty string defaults
                row_with_defaults = {
                    field: result.get(field, "") for field in fieldnames
                }
                writer.writerow(row_with_defaults)

        print(f"\n✓ Saved {len(results)} exhibitors to {output_csv}")
    else:
        print("\nNo results to write!")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(HELP_TEXT)
    else:
        pages_dir = sys.argv[1]
        output_csv = sys.argv[2]

        # Optional limit parameter
        limit = None
        if len(sys.argv) >= 4:
            try:
                limit = int(sys.argv[3])
            except ValueError:
                print(
                    f"Warning: Invalid limit value '{sys.argv[3]}', parsing all files"
                )

        parse_all(pages_dir, output_csv, limit)

        print("\nParsing complete!")
