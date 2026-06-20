#!/usr/bin/env python3
"""
Convert labeled_reviews.json (from the web labeler) back to CSV format.
"""

import csv
import json
from pathlib import Path

INPUT_FILE = 'data/labeled_reviews.json'
OUTPUT_FILE = 'data/steam_reviews_prelabeled_corrected.csv'

def main():
    # Read JSON
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {INPUT_FILE}")
        print("Make sure you've downloaded labeled_reviews.json from the web interface first.")
        return
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {INPUT_FILE}")
        return

    if not reviews:
        print("❌ No reviews found in JSON file")
        return

    print(f"Converting {len(reviews)} labeled reviews to CSV...")

    # Write CSV
    try:
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'label', 'notes', 'game'])
            writer.writeheader()
            writer.writerows(reviews)

        print(f"✅ Saved to {OUTPUT_FILE}")
        print(f"\nLabel distribution:")

        # Count by label
        labels = {}
        for review in reviews:
            label = review.get('label', '')
            labels[label] = labels.get(label, 0) + 1

        for label, count in sorted(labels.items()):
            pct = (count / len(reviews)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")

        print(f"\n✅ Ready to combine with steam_reviews_labeled.csv!")
        print(f"   Command: python3 combine_datasets.py")

    except Exception as e:
        print(f"❌ Error writing CSV: {e}")

if __name__ == '__main__':
    main()
