import csv
import re
from datetime import datetime

INPUT_FILE = 'data/steam_reviews_unlabeled.csv'
OUTPUT_FILE = 'data/steam_reviews_clean.csv'
REMOVED_FILE = 'data/steam_reviews_removed.csv'

def is_ascii_art(text):
    """Detect if text is mostly ASCII art (non-alphanumeric characters)."""
    if len(text) < 50:
        return False

    # Count non-alphanumeric, non-space, non-punctuation characters
    special_chars = len([c for c in text if ord(c) > 127 or c in '░▓█▀▄┌└┘┼╬═║╔╗╚╝'])
    total_chars = len(text)

    # If >20% special/unicode characters, it's likely ASCII art
    if special_chars / total_chars > 0.2:
        return True

    return False

def is_pure_meme(text):
    """Detect meme-only reviews (joke reference with no substance)."""
    # Known meme patterns
    meme_patterns = [
        r'^7 minutes\. 7 minutes',  # MGS reference
        r'^chris punching a boulder',  # RE5 meme (lowercase)
        r'^there is a resident and they are evil',  # Title pun
        r'^put wesker in tekken',  # Off-topic request
        r'^\d+/10$',  # Just a score
        r'^[a-z ]{1,20}$',  # Very short, all lowercase
    ]

    text_lower = text.lower().strip()

    for pattern in meme_patterns:
        if re.match(pattern, text_lower):
            return True

    # If it's 1-2 sentences and clearly a joke/reference with no substance
    sentences = text.split('.')
    if len(sentences) <= 2 and len(text) < 60:
        # Check if it's a known meme format or obvious joke
        if any(phrase in text_lower for phrase in ['chris', 'wesker', 'boulder', 'resident', 'evil']):
            if text.count(' ') <= 3:  # Very short
                return True

    return False

def is_off_topic(text):
    """Detect completely off-topic reviews."""
    # Not about the game itself
    off_topic_patterns = [
        r'put .+ in .+',  # Requests to add to other games
        r'got a cat here',  # Not about the game
        r'friends passing by',  # Not about the game
    ]

    text_lower = text.lower()
    for pattern in off_topic_patterns:
        if re.search(pattern, text_lower):
            return True

    return False

def is_extreme_rage_post(text):
    """Detect extremely angry/unhinged posts (all caps rage, multiple ♥♥♥ censors)."""
    if len(text) < 100:
        return False

    # Count caps, censors, repetitive punctuation
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    censor_count = text.count('♥')
    exclamation_count = text.count('!')

    # If mostly caps + lots of censoring, it's rage posting
    if caps_ratio > 0.4 and censor_count > 3:
        return True

    # All caps + extreme punctuation
    if caps_ratio > 0.5 and (exclamation_count > 5 or censor_count > 5):
        return True

    return False

def should_remove(text):
    """Determine if a review should be removed."""
    if len(text.strip()) < 20:
        return True  # Too short to be meaningful

    if is_ascii_art(text):
        return True

    if is_pure_meme(text):
        return True

    if is_off_topic(text):
        return True

    if is_extreme_rage_post(text):
        return True

    return False

def clean_dataset():
    """Clean the dataset by removing trolls, memes, and off-topic reviews."""
    kept = []
    removed = []

    print("=" * 70)
    print("Steam Reviews Dataset Cleaner")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total_count = 0

            for row in reader:
                total_count += 1
                text = row['text']

                if should_remove(text):
                    removed.append(row)
                    print(f"REMOVED (row {total_count}): {text[:60]}...")
                else:
                    kept.append(row)

        # Save cleaned dataset
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            if kept:
                writer = csv.DictWriter(f, fieldnames=['text', 'label', 'notes', 'game'])
                writer.writeheader()
                writer.writerows(kept)

        # Save removed reviews for inspection
        with open(REMOVED_FILE, 'w', newline='', encoding='utf-8') as f:
            if removed:
                writer = csv.DictWriter(f, fieldnames=['text', 'label', 'notes', 'game'])
                writer.writeheader()
                writer.writerows(removed)

        # Report
        print("\n" + "=" * 70)
        print(f"✅ Cleaning Complete")
        print(f"   Total reviews: {total_count}")
        print(f"   Kept: {len(kept)} ({len(kept)/total_count*100:.1f}%)")
        print(f"   Removed: {len(removed)} ({len(removed)/total_count*100:.1f}%)")
        print(f"\n   Clean dataset: {OUTPUT_FILE}")
        print(f"   Removed reviews: {REMOVED_FILE} (for inspection)")
        print("=" * 70)

        return kept, removed

    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []

if __name__ == '__main__':
    clean_dataset()
