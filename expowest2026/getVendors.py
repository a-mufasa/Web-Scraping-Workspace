# Gets exhibitor IDs from ExpoWest JSON data
import json
import sys

HELP_TEXT = """VENDORS GETTER!
Extracts exhibitor IDs from ExpoWest JSON data!

USAGE: uv run getVendors.py [json_file]

ARGUMENTS
- json_file: The JSON file containing exhibitor data
             (Save the __data JSON object from the exhibitor list page)

Outputs to vendors.txt with one exhibitor ID per line (no duplicates)

Expected JSON structure:
{
  "exhibitors": [
    {
      "id": 13935732,
      "externalId": "RXhoaWJpdG9yXzI0MDgxMjc=",
      "name": "Company Name",
      ...
    }
  ]
}

Comes from: https://npew2026.expofp.com/data/data.js?v=91032864346185168152

Only includes valid exhibitor IDs (starting with RXhoaWJpdG9y = "Exhibitor_" in base64)
Excludes meeting place IDs (TWVldGluZ1BsYWNlX = "MeetingPlace_" in base64)
"""

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == "-h":
        print(HELP_TEXT)
    else:
        try:
            with open(sys.argv[1], "r") as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: File '{sys.argv[1]}' not found.")
            sys.exit(1)

        # Extract exhibitors array
        if "exhibitors" not in json_data:
            print("Error: No 'exhibitors' field found in JSON data.")
            sys.exit(1)

        exhibitors = json_data["exhibitors"]

        exhibitor_ids = []
        seen_ids = set()  # Track duplicates
        skipped_count = 0

        for exhibitor in exhibitors:
            external_id = exhibitor.get("externalId")

            if external_id:
                # Only include valid exhibitor IDs (base64 starting with "RXhoaWJpdG9y" = "Exhibitor_")
                # Skip meeting place IDs (starting with "TWVldGluZ1BsYWNlX" = "MeetingPlace_")
                if (
                    external_id.startswith("RXhoaWJpdG9y")
                    and external_id not in seen_ids
                ):
                    seen_ids.add(external_id)
                    exhibitor_ids.append(external_id)
                else:
                    skipped_count += 1

        print(f"{len(exhibitor_ids)} unique exhibitor IDs found.")
        if skipped_count > 0:
            print(f"{skipped_count} non-exhibitor IDs skipped (meeting places, etc.).")

        if exhibitor_ids:
            output_file = sys.argv[1].replace(".json", ".txt")
            with open(output_file, "w") as f:
                f.write("\n".join(exhibitor_ids))
            print(f"Saved to {output_file}")
        else:
            print("No exhibitor IDs found. Please check the JSON structure.")
