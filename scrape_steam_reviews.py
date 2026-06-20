import csv
import time
from datetime import datetime

import requests

# ============================================================================
# Configuration
# ============================================================================

# Resident Evil Remakes & Games on Steam
GAME_APP_IDS = [
    304240,  # Resident Evil (2015 Remake)
    883710,  # Resident Evil 2 (2019 Remake)
    952060,  # Resident Evil 3 (2020 Remake)
    2050650,  # Resident Evil 4 (2023 Remake)
    21690,  # Resident Evil 5
    # Optional: Add more if needed
    # 221040,    # Resident Evil 6
    # 418370,    # Resident Evil 7 Biohazard
]

TARGET_COUNT = 250  # Aim for 250 reviews
OUTPUT_FILE = "data/steam_reviews_unlabeled.csv"
REQUEST_DELAY = 0.5  # Seconds between requests (Steam is lenient)

# Steam Store Reviews API endpoint (correct URL)
STEAM_API_URL = "https://store.steampowered.com/appreviews/{app_id}"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_steam_reviews(app_id, target_count=TARGET_COUNT):
    """
    Fetch reviews from Steam Community API for a specific game.
    Returns list of review texts.
    """
    reviews = []
    cursor = "*"
    request_count = 0

    print(f"\nFetching reviews for App ID: {app_id}")
    print("=" * 70)

    try:
        while len(reviews) < target_count and cursor:
            params = {
                "json": 1,
                "filter": "recent",
                "language": "english",
                "review_type": "all",
                "purchases_only": 0,
                "cursor": cursor,
                "num_per_page": 100,
            }

            print(
                f"Request #{request_count + 1}: Fetching up to 100 reviews...", end=""
            )

            url = STEAM_API_URL.format(app_id=app_id)
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract reviews from this batch
            if "reviews" not in data:
                print(" ❌ No reviews found")
                break

            batch_reviews = data["reviews"]
            batch_count = 0

            for review in batch_reviews:
                review_text = review.get("review", "").strip()

                # Filter: skip very short reviews (one-word hype)
                if len(review_text) < 30:
                    continue

                reviews.append(
                    {
                        "text": review_text,
                        "label": "",  # You will label these
                        "game": get_game_name(app_id),
                        "notes": "",
                    }
                )
                batch_count += 1

            print(f" Got {batch_count} valid reviews (total: {len(reviews)})")

            # Get cursor for next page
            cursor = data.get("cursor", "")

            request_count += 1

            # Rate limiting
            if len(reviews) < target_count and cursor:
                time.sleep(REQUEST_DELAY)

            if request_count > 10:  # Safety limit to avoid too many requests
                print("Reached request limit. Stopping.")
                break

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
    except KeyError as e:
        print(f"\n❌ Unexpected response format: {e}")

    return reviews


def get_game_name(app_id):
    """Try to get the game name from Steam (optional)."""
    game_names = {
        304240: "Resident Evil (2015 Remake)",
        883710: "Resident Evil 2 (2019 Remake)",
        952060: "Resident Evil 3 (2020 Remake)",
        2050650: "Resident Evil 4 (2023 Remake)",
        21690: "Resident Evil 5",
        221040: "Resident Evil 6",
        418370: "Resident Evil 7 Biohazard",
    }
    return game_names.get(app_id, f"App {app_id}")


def fetch_all_reviews(app_ids, target_count=TARGET_COUNT):
    """Fetch reviews from multiple games, balanced across all."""
    all_reviews = []

    # Calculate reviews per game to balance across all games
    reviews_per_game = target_count // len(app_ids)

    print(
        f"\nPlan: Fetch ~{reviews_per_game} reviews from each of {len(app_ids)} games"
    )
    print("=" * 70)

    for i, app_id in enumerate(app_ids):
        game_name = get_game_name(app_id)
        print(f"\nGame {i + 1}/{len(app_ids)}: {game_name}")

        reviews = fetch_steam_reviews(app_id, target_count=reviews_per_game)

        if reviews:
            print(f"✅ Collected {len(reviews)} reviews from {game_name}")
            all_reviews.extend(reviews)
        else:
            print(f"⚠️  No reviews fetched for {game_name}")

        # Respectful delay between different games
        if i < len(app_ids) - 1:
            time.sleep(1)

    return all_reviews


def save_to_csv(reviews, filename=OUTPUT_FILE):
    """Save reviews to CSV with the required columns."""
    if not reviews:
        print("No reviews to save.")
        return

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "label", "notes", "game"])
            writer.writeheader()
            writer.writerows(reviews)

        print(f"\n✅ Saved {len(reviews)} reviews to {filename}\n")
        print(f"Next steps:")
        print(f"1. Open {filename}")
        print(f"2. Read each review and assign a label from your taxonomy")
        print(f"3. Add notes for difficult cases")
        print(f"4. Ensure label distribution: no label > 70% of total")

    except IOError as e:
        print(f"❌ Error saving file: {e}")


def main():
    print("=" * 70)
    print("Steam Reviews Scraper")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print(f"\nTarget: {TARGET_COUNT} reviews")
    print(
        f"Games to scrape: {[get_game_name(app_id) for app_id in GAME_APP_IDS[:3]]}..."
    )
    print("\nTo change games, edit GAME_APP_IDS in the script")
    print("Find app IDs at: https://steamdb.info/")

    # Fetch reviews
    reviews = fetch_all_reviews(GAME_APP_IDS, target_count=TARGET_COUNT)

    if reviews:
        print(f"\n✅ Successfully fetched {len(reviews)} reviews\n")
        save_to_csv(reviews)
    else:
        print("\n❌ No reviews were fetched.")

    print("=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
