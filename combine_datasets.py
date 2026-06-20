#!/usr/bin/env python3
"""
Combine steam_reviews_labeled.csv and steam_reviews_prelabeled_corrected.csv
into a final complete dataset.
"""

import csv

LABELED_FILE = 'data/steam_reviews_labeled.csv'
CORRECTED_FILE = 'data/steam_reviews_prelabeled_corrected.csv'
OUTPUT_FILE = 'data/steam_reviews_final.csv'

def main():
    print("Combining datasets...")

    # Read labeled file
    labeled_reviews = []
    try:
        with open(LABELED_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                labeled_reviews.append(row)
    except FileNotFoundError:
        print(f"❌ File not found: {LABELED_FILE}")
        return

    print(f"  Loaded {len(labeled_reviews)} from {LABELED_FILE}")

    # Read corrected prelabeled file
    corrected_reviews = []
    try:
        with open(CORRECTED_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                corrected_reviews.append(row)
    except FileNotFoundError:
        print(f"❌ File not found: {CORRECTED_FILE}")
        print("   Make sure you've run convert_labeled_json_to_csv.py first")
        return

    print(f"  Loaded {len(corrected_reviews)} from {CORRECTED_FILE}")

    # Combine
    all_reviews = labeled_reviews + corrected_reviews
    total = len(all_reviews)

    print(f"\n✅ Combined {total} total reviews")

    # Save final file
    try:
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'label', 'notes', 'game'])
            writer.writeheader()
            writer.writerows(all_reviews)

        print(f"✅ Saved to {OUTPUT_FILE}")

        # Summary
        print(f"\n{'='*70}")
        print("FINAL DATASET SUMMARY")
        print(f"{'='*70}")
        print(f"\nTotal reviews: {total}")

        # Count by label
        labels = {}
        for review in all_reviews:
            label = review.get('label', '')
            labels[label] = labels.get(label, 0) + 1

        print(f"\nLabel distribution:")
        for label, count in sorted(labels.items()):
            pct = (count / total) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")

        # Check balance
        max_label = max(labels.values())
        max_pct = (max_label / total) * 100

        print(f"\nBalance check:")
        if max_pct > 70:
            print(f"  ⚠️  Highest label is {max_pct:.1f}% (should be <70%)")
        else:
            print(f"  ✅ Balanced - highest label is {max_pct:.1f}%")

        print(f"\n✅ Ready for M4 (fine-tuning)!")

    except Exception as e:
        print(f"❌ Error writing final file: {e}")

if __name__ == '__main__':
    main()
