import asyncio
import json
import sys
import uuid
from pathlib import Path

import httpx

HELP_TEXT = """NHS GraphQL Scraper
Fetches exhibitor JSON from Reed Expo GraphQL using organisation IDs.

USAGE: python3 scrape.py [vendors_file (optional)] [event_edition_id (optional)] [concurrency (optional)]

- vendors_file (optional) = text file with one organisation_id per line; defaults to vendors.txt
- event_edition_id (optional) = event edition id; defaults to eve-e3691757-182e-41e8-a5c2-ec941bc13860
- concurrency (optional) = concurrent requests; defaults to 15
"""

GRAPHQL_URL = "https://api.reedexpo.com/graphql/"
DEFAULT_CLIENT_ID = "uhQVcmxLwXAjVtVpTvoerERiZSsNz0om"
DEFAULT_VENDORS_FILE = "vendors.txt"
DEFAULT_EVENT_EDITION_ID = "eve-e3691757-182e-41e8-a5c2-ec941bc13860"
DEFAULT_CONCURRENCY = 15

GRAPHQL_QUERY = """
query ($eventEditionId: String!, $organisationId: String!) {
  exhibitingOrganisation(eventEditionId: $eventEditionId, organisationId: $organisationId) {
    id
    productsAndServices {
      id
    }
    socialMedia {
      url
      name
    }
    isNew
    organisationId
    accompanyingWebsiteUrl
    packageId
    companyName
    contactEmail
    website
    phone
    hideAddress
    extraCharacteristics {
      id
    }
    multilingual {
      logoUrl
      coverImageUrl
      locale
      displayName
      description
      showObjective
      sortAlias
      representedBrands {
        name
      }
      addressLine1
      addressLine2
      stateProvince
      city
      countryCode
      postcode
      country
      additionalAddresses {
        addressLine1
        addressLine2
        stateProvince
        city
        countryCode
        postcode
      }
    }
    exhibitingProducers {
      id
      firstName
      lastName
    }
    representedProducers {
      id
      firstName
      lastName
    }
    directors
    filterCategories {
      multilingual {
        name
        locale
      }
      responses {
        answerId
        parentId
        taxonomyId
        multilingual {
          name
          locale
        }
      }
      id
    }
    products(includeUnpublished: false) {
      id
      exhibitingOrganisationId
      imageUrl
      isInnovative
      isNew
      videoId
      video {
        id
        defaultThumbnailUrl
        customThumbnailUrl
        status
      }
      isPublished
      lastUpdatedAt
      producerDetails {
        id
        firstName
        lastName
      }
      multilingual {
        title
        description
        locale
      }
      filterAttributes {
        id
        questionText {
          locale
          name
        }
        textualResponses {
          locale
          textResponse
        }
        responses {
          answerId
          answerText {
            locale
            name
          }
        }
        sortOrder
      }
      attributes {
        id
        questionText {
          locale
          name
        }
        responses {
          answerId
          answerText {
            locale
            name
          }
        }
        textualResponses {
          locale
          textResponse
        }
        sortOrder
      }
    }
    stands {
      name
    }
    sharers {
      id
      organisationGuid
      name
      isActive
      packageId
      multilingual {
        name
        locale
      }
    }
    mainStandHolder {
      organisationGuid
      id
      packageId
      multilingual {
        name
        locale
      }
      sharers {
        id
        organisationGuid
        name
        isActive
        packageId
        multilingual {
          name
          locale
        }
      }
    }
  }
}
""".strip()


def load_organisation_ids(vendors_file):
    with open(vendors_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_headers(client_id):
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://www.nhsconcepttocommerce.com",
        "referer": "https://www.nhsconcepttocommerce.com/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        ),
        "x-clientid": client_id,
    }


async def fetch_one(client, event_edition_id, organisation_id, semaphore):
    async with semaphore:
        payload = {
            "query": GRAPHQL_QUERY,
            "variables": {
                "eventEditionId": event_edition_id,
                "organisationId": organisation_id,
            },
        }

        headers = {"x-correlationid": str(uuid.uuid4())}

        try:
            response = await client.post(
                GRAPHQL_URL, json=payload, headers=headers, timeout=40
            )
            response.raise_for_status()
            body = response.json()
            return organisation_id, body, None
        except Exception as exc:
            return organisation_id, None, str(exc)


async def scrape_all(organisation_ids, event_edition_id, concurrency, client_id):
    pages_dir = Path("pages")
    pages_dir.mkdir(exist_ok=True)

    semaphore = asyncio.Semaphore(concurrency)
    base_headers = build_headers(client_id)

    success_count = 0
    error_count = 0

    async with httpx.AsyncClient(
        headers=base_headers, follow_redirects=True, timeout=40
    ) as client:
        tasks = [
            fetch_one(client, event_edition_id, organisation_id, semaphore)
            for organisation_id in organisation_ids
        ]

        print(f"Fetching {len(tasks)} organisations with concurrency={concurrency}\n")

        completed = 0
        for coro in asyncio.as_completed(tasks):
            organisation_id, body, error = await coro
            completed += 1

            if error:
                error_count += 1
                print(f"[{completed}/{len(tasks)}] ERROR {organisation_id}: {error}")
            else:
                output_file = pages_dir / f"{organisation_id}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(body, f, ensure_ascii=False, indent=2)

                if not isinstance(body, dict):
                    error_count += 1
                    print(
                        f"[{completed}/{len(tasks)}] Invalid response for {organisation_id}"
                    )
                elif body.get("errors"):
                    error_count += 1
                    print(
                        f"[{completed}/{len(tasks)}] GraphQL errors for {organisation_id}"
                    )
                elif body.get("data", {}).get("exhibitingOrganisation"):
                    success_count += 1
                else:
                    error_count += 1
                    print(
                        f"[{completed}/{len(tasks)}] Missing data for {organisation_id}"
                    )

            if completed % 25 == 0 or completed == len(tasks):
                print(
                    f"Progress: {completed}/{len(tasks)} complete "
                    f"(success={success_count}, errors={error_count})"
                )

    print("\nDone")
    print(f"Saved JSON files to: {pages_dir}")
    print(f"Successful records: {success_count}")
    print(f"Errors/missing records: {error_count}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print(HELP_TEXT)
        return

    vendors_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VENDORS_FILE
    event_edition_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_EVENT_EDITION_ID

    try:
        concurrency = int(sys.argv[3])
    except (IndexError, ValueError):
        concurrency = DEFAULT_CONCURRENCY

    organisation_ids = load_organisation_ids(vendors_file)
    if not organisation_ids:
        print(f"No organisation IDs found in {vendors_file}")
        return

    print(f"Loaded {len(organisation_ids)} organisation IDs from {vendors_file}")
    print(f"Event Edition ID: {event_edition_id}")

    client_id = DEFAULT_CLIENT_ID
    asyncio.run(scrape_all(organisation_ids, event_edition_id, concurrency, client_id))


if __name__ == "__main__":
    main()
