import csv
import json
import sys
from pathlib import Path

HELP_TEXT = """NHS Parser
Parses GraphQL JSON files and writes a flattened CSV.

USAGE: python3 parse.py [pages_dir (optional)] [output_csv (optional)] [preferred_locale (optional)]

- pages_dir (optional) = folder with JSON files from scrape.py; defaults to pages
- output_csv (optional) = output CSV filename; defaults to nhs_exhibitors.csv
- preferred_locale (optional) = locale preference, defaults to en-us
"""

DEFAULT_PAGES_DIR = "pages"
DEFAULT_OUTPUT_CSV = "nhs_exhibitors.csv"
DEFAULT_LOCALE = "en-us"


def normalize_locale(value):
    return (value or "").strip().lower()


def pick_locale_item(items, preferred_locale="en-us"):
    """Pick the best multilingual entry for a preferred locale."""
    if not isinstance(items, list) or not items:
        return {}

    preferred_locale = normalize_locale(preferred_locale)

    for item in items:
        if normalize_locale(item.get("locale")) == preferred_locale:
            return item

    for item in items:
        if normalize_locale(item.get("locale")).startswith("en"):
            return item

    return items[0]


def unique_join(values, sep="; "):
    seen = set()
    cleaned = []
    for value in values:
        text = str(value).strip() if value is not None else ""
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return sep.join(cleaned)


def get_social_map(social_media):
    social_map = {}
    other = []

    for item in social_media or []:
        name = (item.get("name") or "").strip().lower()
        url = (item.get("url") or "").strip()
        if not url:
            continue

        if name in ["facebook", "twitter", "linkedin", "instagram", "youtube"]:
            social_map[name] = url
        else:
            other.append(f"{item.get('name', 'OTHER')}:{url}")

    social_map["other"] = unique_join(other)
    return social_map


def extract_filter_categories(filter_categories, preferred_locale="en-us"):
    category_map = {}

    for category in filter_categories or []:
        category_name = (
            pick_locale_item(category.get("multilingual", []), preferred_locale)
            .get("name", "")
            .strip()
        )
        if not category_name:
            continue

        answers = []
        for response in category.get("responses") or []:
            answer_name = (
                pick_locale_item(response.get("multilingual", []), preferred_locale)
                .get("name", "")
                .strip()
            )
            if answer_name:
                answers.append(answer_name)

        category_map[category_name] = unique_join(answers)

    return category_map


def extract_products(products, preferred_locale="en-us"):
    titles = []
    descriptions = []
    product_category_answers = []

    for product in products or []:
        selected_locale = pick_locale_item(
            product.get("multilingual", []), preferred_locale
        )
        title = (selected_locale.get("title") or "").strip()
        description = (
            (selected_locale.get("description") or "").replace("\n", " ").strip()
        )

        if title:
            titles.append(title)
        if description:
            descriptions.append(description)

        for attr_group in [
            product.get("filterAttributes") or [],
            product.get("attributes") or [],
        ]:
            for attr in attr_group:
                for response in attr.get("responses") or []:
                    answer_text = (
                        pick_locale_item(
                            response.get("answerText", []), preferred_locale
                        )
                        .get("name", "")
                        .strip()
                    )
                    if answer_text:
                        product_category_answers.append(answer_text)

    return {
        "titles": unique_join(titles),
        "descriptions": unique_join(descriptions),
        "categories": unique_join(product_category_answers),
        "count": len(products or []),
    }


def parse_exhibitor(payload, preferred_locale="en-us"):
    exhibitor = payload.get("data", {}).get("exhibitingOrganisation")
    if not exhibitor:
        return None

    locale_entry = pick_locale_item(exhibitor.get("multilingual", []), preferred_locale)
    social = get_social_map(exhibitor.get("socialMedia") or [])
    category_map = extract_filter_categories(
        exhibitor.get("filterCategories") or [], preferred_locale
    )
    product_data = extract_products(exhibitor.get("products") or [], preferred_locale)

    stands = [
        stand.get("name", "").strip()
        for stand in exhibitor.get("stands") or []
        if stand.get("name")
    ]
    brands = [
        brand.get("name", "").strip()
        for brand in locale_entry.get("representedBrands") or []
        if brand.get("name")
    ]

    address_parts = [
        locale_entry.get("addressLine1", ""),
        locale_entry.get("addressLine2", ""),
        locale_entry.get("city", ""),
        locale_entry.get("stateProvince", ""),
        locale_entry.get("postcode", ""),
        locale_entry.get("country", ""),
    ]

    return {
        "organisation_id": exhibitor.get("organisationId", ""),
        "exhibiting_organisation_id": exhibitor.get("id", ""),
        "company_name": exhibitor.get("companyName", ""),
        "display_name": locale_entry.get("displayName", ""),
        "sort_alias": locale_entry.get("sortAlias", ""),
        "booth_numbers": unique_join(stands),
        "description": (locale_entry.get("description") or "")
        .replace("\n", " ")
        .strip(),
        "show_objective": (locale_entry.get("showObjective") or "")
        .replace("\n", " ")
        .strip(),
        "website": exhibitor.get("website", ""),
        "accompanying_website_url": exhibitor.get("accompanyingWebsiteUrl", ""),
        "contact_email": exhibitor.get("contactEmail", ""),
        "phone": exhibitor.get("phone", ""),
        "address_line_1": locale_entry.get("addressLine1", ""),
        "address_line_2": locale_entry.get("addressLine2", ""),
        "city": locale_entry.get("city", ""),
        "state_province": locale_entry.get("stateProvince", ""),
        "postcode": locale_entry.get("postcode", ""),
        "country_code": locale_entry.get("countryCode", ""),
        "country": locale_entry.get("country", ""),
        "full_address": unique_join(address_parts, sep=", "),
        "logo_url": locale_entry.get("logoUrl", ""),
        "cover_image_url": locale_entry.get("coverImageUrl", ""),
        "represented_brands": unique_join(brands),
        "facebook": social.get("facebook", ""),
        "twitter": social.get("twitter", ""),
        "linkedin": social.get("linkedin", ""),
        "instagram": social.get("instagram", ""),
        "youtube": social.get("youtube", ""),
        "social_other": social.get("other", ""),
        "directory_categories": unique_join(
            [f"{k}: {v}" if v else k for k, v in category_map.items()]
        ),
        "product_titles": product_data["titles"],
        "product_descriptions": product_data["descriptions"],
        "product_categories": product_data["categories"],
        "product_count": product_data["count"],
        "is_new": exhibitor.get("isNew", ""),
        "package_id": exhibitor.get("packageId", ""),
        "hide_address": exhibitor.get("hideAddress", ""),
        "locale_used": locale_entry.get("locale", ""),
    }


def parse_all(pages_dir, output_csv, preferred_locale="en-us"):
    pages_path = Path(pages_dir)
    if not pages_path.exists():
        print(f"Error: Directory does not exist: {pages_dir}")
        return

    json_files = sorted(pages_path.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {pages_dir}")
        return

    print(f"Found {len(json_files)} JSON files")

    rows = []
    skipped = 0

    for idx, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as exc:
            print(f"[{idx}/{len(json_files)}] Failed to read {json_file.name}: {exc}")
            skipped += 1
            continue

        row = parse_exhibitor(payload, preferred_locale=preferred_locale)
        if row is None:
            skipped += 1
            print(f"[{idx}/{len(json_files)}] No exhibitor data in {json_file.name}")
            continue

        rows.append(row)

        if idx % 25 == 0 or idx == len(json_files):
            print(f"Parsed {idx}/{len(json_files)} files")

    if not rows:
        print("No parsed rows to write")
        return

    fieldnames = list(rows[0].keys())

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} exhibitors to {output_csv}")
    if skipped:
        print(f"Skipped {skipped} files")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print(HELP_TEXT)
        return

    pages_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PAGES_DIR
    output_csv = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_CSV
    preferred_locale = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_LOCALE

    parse_all(pages_dir, output_csv, preferred_locale)


if __name__ == "__main__":
    main()
