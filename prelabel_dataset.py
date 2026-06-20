import csv
import sys
from datetime import datetime

# For Claude API calls (local inference)
import subprocess
import json

INPUT_FILE = 'data/steam_reviews_clean.csv'
OUTPUT_FILE = 'data/steam_reviews_prelabeled.csv'
DIFFICULT_CASES_FILE = 'data/difficult_cases.txt'

LABEL_DEFINITIONS = """
You are labeling Steam game reviews for discourse quality. Use EXACTLY ONE of these three labels:

1. design_discussion - The review discusses specific game mechanics, level design, puzzle design, difficulty balance, visual/audio design, control systems, or pacing with concrete observations about how those systems work.

2. opinion_judgment - The review states an overall quality assessment (good/bad/great/terrible) without explaining why through specific mechanics, design observations, or evidence.

3. personal_experience - The review focuses on the player's emotional journey, sensory reaction, personal feelings, or how the game made them feel during gameplay.

RULES:
- Assign EXACTLY ONE label per review
- If a review could belong to multiple labels, focus on the PRIMARY focus:
  * If it mainly describes game systems → design_discussion
  * If it mainly asserts quality → opinion_judgment
  * If it mainly describes player feelings → personal_experience
- For borderline cases, output the label but mark it with [UNCERTAIN] prefix
- Output format: ONLY the label name (or [UNCERTAIN]label_name)
- Do not output explanations, just the label
"""

def batch_reviews(reviews, batch_size=30):
    """Break reviews into batches."""
    for i in range(0, len(reviews), batch_size):
        yield reviews[i:i + batch_size]

def prelabel_batch(batch):
    """Use Claude via subprocess to pre-label a batch of reviews."""
    reviews_text = "\n\n".join([f"Review {i+1}: {r['text']}" for i, r in enumerate(batch)])

    prompt = f"""{LABEL_DEFINITIONS}

Now label these reviews. Output one label per line, in order:

{reviews_text}"""

    try:
        # Call Claude via command line (claude-code CLI)
        result = subprocess.run(
            ['claude', 'ask', prompt],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"Error calling Claude: {result.stderr}")
            return None

        output = result.stdout.strip()
        labels = [line.strip() for line in output.split('\n') if line.strip()]

        return labels[:len(batch)]

    except Exception as e:
        print(f"Error in prelabel_batch: {e}")
        return None

def mark_uncertain(label):
    """Check if label is marked as uncertain."""
    return label.startswith('[UNCERTAIN]')

def get_clean_label(label):
    """Remove [UNCERTAIN] prefix if present."""
    if label.startswith('[UNCERTAIN]'):
        return label.replace('[UNCERTAIN]', '')
    return label

def main():
    print("=" * 70)
    print("Pre-labeling Steam Reviews Dataset")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Read reviews
    reviews = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                reviews.append(row)
    except Exception as e:
        print(f"Error reading {INPUT_FILE}: {e}")
        return

    print(f"\nLoaded {len(reviews)} reviews to pre-label")
    print("\nNote: This requires Claude API access via 'claude' CLI command")
    print("If not available, you can pre-label manually or skip this step\n")

    # Pre-label in batches
    all_labeled = []
    label_counts = {'design_discussion': 0, 'opinion_judgment': 0, 'personal_experience': 0, 'uncertain': 0}
    difficult_cases = []

    batch_num = 0
    for batch in batch_reviews(reviews, batch_size=30):
        batch_num += 1
        print(f"Batch {batch_num}: Pre-labeling {len(batch)} reviews...", end='', flush=True)

        labels = prelabel_batch(batch)

        if not labels or len(labels) != len(batch):
            print(" ⚠️ Claude unavailable, using manual placeholders")
            # Use placeholder - user will fill in manually
            for review in batch:
                all_labeled.append({
                    'text': review['text'],
                    'label': '',  # Empty - user will fill
                    'notes': '[PRE-LABEL PENDING]',
                    'game': review['game'],
                    'pre_labeled': 'no'
                })
            continue

        print(f" Got {len(labels)} labels")

        # Process labels
        for i, review in enumerate(batch):
            label_raw = labels[i]
            is_uncertain = mark_uncertain(label_raw)
            label_clean = get_clean_label(label_raw)

            # Validate label
            if label_clean not in ['design_discussion', 'opinion_judgment', 'personal_experience']:
                label_clean = ''  # Invalid, user will review
                is_uncertain = True

            # Count
            if is_uncertain:
                label_counts['uncertain'] += 1
                difficult_cases.append({
                    'text': review['text'][:100] + '...',
                    'pre_label': label_clean,
                    'status': 'uncertain',
                    'game': review['game']
                })
            else:
                label_counts[label_clean] += 1

            all_labeled.append({
                'text': review['text'],
                'label': label_clean,
                'notes': '[UNCERTAIN]' if is_uncertain else '',
                'game': review['game'],
                'pre_labeled': 'yes'
            })

    # Save pre-labeled dataset
    try:
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'label', 'notes', 'game', 'pre_labeled'])
            writer.writeheader()
            writer.writerows(all_labeled)
        print(f"\n✅ Saved pre-labeled dataset to {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Error saving {OUTPUT_FILE}: {e}")
        return

    # Save difficult cases
    try:
        with open(DIFFICULT_CASES_FILE, 'w', encoding='utf-8') as f:
            f.write("DIFFICULT CASES FOR MANUAL REVIEW\n")
            f.write("=" * 70 + "\n\n")
            for i, case in enumerate(difficult_cases[:20], 1):  # Top 20
                f.write(f"{i}. Game: {case['game']}\n")
                f.write(f"   Text: {case['text']}\n")
                f.write(f"   Pre-label: {case['pre_label']}\n")
                f.write(f"   Status: {case['status']}\n\n")
        print(f"✅ Saved difficult cases to {DIFFICULT_CASES_FILE}")
    except Exception as e:
        print(f"⚠️  Could not save difficult cases: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("PRE-LABELING SUMMARY")
    print("=" * 70)
    print(f"\nTotal reviews pre-labeled: {len(all_labeled)}")
    print(f"\nLabel Distribution:")
    print(f"  Design Discussion:    {label_counts['design_discussion']:3d} ({label_counts['design_discussion']/len(all_labeled)*100:5.1f}%)")
    print(f"  Opinion/Judgment:     {label_counts['opinion_judgment']:3d} ({label_counts['opinion_judgment']/len(all_labeled)*100:5.1f}%)")
    print(f"  Personal Experience:  {label_counts['personal_experience']:3d} ({label_counts['personal_experience']/len(all_labeled)*100:5.1f}%)")
    print(f"  Uncertain/Review:     {label_counts['uncertain']:3d} ({label_counts['uncertain']/len(all_labeled)*100:5.1f}%)")

    print(f"\n✅ Next step: Open {OUTPUT_FILE} and review/correct each label")
    print("=" * 70)

if __name__ == '__main__':
    main()
