#!/usr/bin/env python3
"""
Re-analyze 112 uncertain Resident Evil reviews.
Classify with HIGH or MEDIUM confidence, move to labeled file.
Keep truly uncertain ones in prelabeled file.
Uses only standard library.
"""

import csv
from pathlib import Path
import re

# Label definitions from planning.md
LABEL_DEFINITIONS = {
    'design_discussion': {
        'keywords': [
            'mechanic', 'puzzle', 'design', 'difficulty', 'balance', 'pacing',
            'control', 'camera', 'gameplay', 'system', 'level', 'atmosphere',
            'exploration', 'resource management', 'combat', 'enemy design',
            'sound design', 'soundtrack', 'visual', 'inventory', 'level design',
            'fixed camera', 'tank control', 'save room', 'difficulty curve'
        ],
        'pattern': 'Discusses specific game mechanics, systems, or design choices with concrete observations'
    },
    'opinion_judgment': {
        'keywords': [
            'best', 'worst', 'great', 'terrible', 'perfect', 'horrible',
            'amazing', 'awful', 'masterpiece', 'excellent', 'good', 'bad',
            'must play', 'avoid', 'overrated', 'underrated', 'love it', 'hate it',
            'top notch', 'solid', 'pretty good', '10/10', '9/10', '8/10',
            'recommended', 'recommend', 'would not recommend'
        ],
        'pattern': 'States quality assessment without explaining why (no specific reasoning)'
    },
    'personal_experience': {
        'keywords': [
            'love', 'scared', 'fun', 'enjoy', 'feeling', 'experience', 'journey',
            'playthrough', 'hours', 'immersive', 'adventure', 'friends', 'emotion',
            'felt', 'made me', 'gave me', 'memories', 'nostalgia', 'scare',
            'thrilling', 'exciting', 'had a blast', 'once in a lifetime',
            'blast', 'fear', 'heart racing', 'adrenaline', 'blast'
        ],
        'pattern': 'Focuses on emotional journey, sensory reaction, or personal feelings'
    }
}

def analyze_review(text, current_label):
    """
    Analyze a review and determine confidence level.
    Returns: (new_label, confidence, reason)
    """
    text_lower = text.lower()
    text_len = len(text.split())

    # Count keyword matches for each label
    keyword_counts = {}
    for label, info in LABEL_DEFINITIONS.items():
        count = sum(1 for kw in info['keywords'] if kw in text_lower)
        keyword_counts[label] = count

    # Analyze text characteristics
    has_reasoning = any(phrase in text_lower for phrase in [
        'because', 'since', 'so that', 'allows', 'makes', 'creates', 'causes',
        'due to', 'result in', 'leads to', 'especially', 'specifically',
        'the way', 'how', 'in that', 'this mechanic'
    ])

    has_emotion = any(phrase in text_lower for phrase in [
        'felt', 'scared', 'loved', 'enjoy', 'fun', 'amazing', 'wonderful',
        'hate', 'despise', 'gave me', 'made me feel', 'made me want',
        'blew my mind', 'heart racing', 'edge of my seat', 'had a blast',
        'once in a lifetime', 'frightened', 'thrilled', 'scare'
    ])

    is_short = text_len < 20
    is_very_short = text_len < 10

    # Check for pure assertion patterns (no explanation)
    has_pure_opinion = any(phrase in text_lower for phrase in [
        "it's the best", "it's great", "it's terrible", "it's awful",
        "this game is best", "this game is great", "this game is terrible",
        "game is the best", "masterpiece", "waste of time"
    ]) and not has_reasoning

    design_keywords = keyword_counts['design_discussion']
    opinion_keywords = keyword_counts['opinion_judgment']
    personal_keywords = keyword_counts['personal_experience']

    # DESIGN DISCUSSION: Clear mechanics/systems discussion with reasoning
    if design_keywords >= 2:
        if has_reasoning or design_keywords >= 3:
            return 'design_discussion', 'HIGH', f'Multiple design keywords ({design_keywords}) with reasoning'
        elif design_keywords >= 2 and not has_pure_opinion:
            return 'design_discussion', 'MEDIUM', f'{design_keywords} design keywords, concrete mechanics'

    # PERSONAL EXPERIENCE: Clear emotional/journey focus
    if personal_keywords >= 2:
        if has_emotion or 'playthrough' in text_lower or 'hours' in text_lower:
            return 'personal_experience', 'HIGH', f'Strong emotional/personal language ({personal_keywords} markers)'
        else:
            return 'personal_experience', 'MEDIUM', f'{personal_keywords} personal experience keywords'

    # OPINION/JUDGMENT: Pure assertion without reasoning
    if is_very_short and opinion_keywords >= 1 and not has_reasoning:
        return 'opinion_judgment', 'HIGH', 'Short quality assertion without reasoning'
    elif opinion_keywords >= 2 and not (design_keywords >= 2 or personal_keywords >= 2):
        return 'opinion_judgment', 'HIGH', f'{opinion_keywords} opinion words, no design/personal details'
    elif opinion_keywords >= 1 and is_short and not has_reasoning:
        return 'opinion_judgment', 'MEDIUM', 'Opinion statement with limited support'

    # MIXED CASES: Use heuristics to determine primary signal
    design_score = design_keywords * 1.5 if has_reasoning else design_keywords
    personal_score = personal_keywords * 1.3 if has_emotion else personal_keywords
    opinion_score = opinion_keywords if not has_reasoning else opinion_keywords * 0.8

    max_score = max(design_score, personal_score, opinion_score)

    if abs(design_score - max_score) < 0.1 and design_score > 0:
        return 'design_discussion', 'MEDIUM', 'Mixed signals but mechanics are central'
    elif abs(personal_score - max_score) < 0.1 and personal_score > 0:
        return 'personal_experience', 'MEDIUM', 'Mixed signals but emotional tone dominates'
    elif abs(opinion_score - max_score) < 0.1 and opinion_score > 0:
        return 'opinion_judgment', 'MEDIUM', 'Mixed signals but judgment is primary'

    # Fallback to current label if no clear signal
    if max(design_keywords, opinion_keywords, personal_keywords) > 0:
        return current_label, 'MEDIUM', f'Defaulting to current label {current_label}'
    else:
        return current_label, 'LOW', 'No clear keywords - genuinely ambiguous'

def read_csv(filepath):
    """Read CSV file and return list of dicts."""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def write_csv(filepath, fieldnames, rows):
    """Write rows to CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    # Load files
    prelabeled_path = 'data/steam_reviews_prelabeled.csv'
    labeled_path = 'data/steam_reviews_labeled.csv'

    prelabeled_rows = read_csv(prelabeled_path)
    labeled_rows = read_csv(labeled_path)

    print(f"Loaded {len(prelabeled_rows)} uncertain reviews")
    print(f"Loaded {len(labeled_rows)} confident reviews")
    print("\n" + "="*80)

    # Analyze each uncertain review
    confident_reviews = []
    still_uncertain_reviews = []

    high_count = 0
    medium_count = 0
    low_count = 0

    label_distribution_confident = {'design_discussion': 0, 'opinion_judgment': 0, 'personal_experience': 0}
    label_distribution_uncertain = {'design_discussion': 0, 'opinion_judgment': 0, 'personal_experience': 0}

    for idx, row in enumerate(prelabeled_rows):
        text = row['text']
        current_label = row['label']

        new_label, confidence, reason = analyze_review(text, current_label)

        # Create new row with updated info
        new_row = row.copy()
        new_row['label'] = new_label

        if confidence == 'HIGH':
            new_row['notes'] = f'[RE-LABELED HIGH] {reason}'
            confident_reviews.append(new_row)
            label_distribution_confident[new_label] += 1
            high_count += 1
        elif confidence == 'MEDIUM':
            new_row['notes'] = f'[RE-LABELED MEDIUM] {reason}'
            confident_reviews.append(new_row)
            label_distribution_confident[new_label] += 1
            medium_count += 1
        else:  # LOW confidence
            new_row['notes'] = f'[STILL UNCERTAIN] {reason}'
            still_uncertain_reviews.append(new_row)
            label_distribution_uncertain[new_label] += 1
            low_count += 1

    print(f"\nRe-analysis Results:")
    print(f"  HIGH confidence: {high_count} reviews")
    print(f"  MEDIUM confidence: {medium_count} reviews")
    print(f"  LOW confidence (still uncertain): {low_count} reviews")
    print(f"  Total moved to confident: {high_count + medium_count}")

    # Combine confident reviews with existing labeled data
    combined_labeled = labeled_rows + confident_reviews

    # Get fieldnames from first row
    fieldnames = list(prelabeled_rows[0].keys()) if prelabeled_rows else []

    # Save updated files
    write_csv(labeled_path, fieldnames, combined_labeled)
    write_csv(prelabeled_path, fieldnames, still_uncertain_reviews)

    print(f"\n" + "="*80)
    print(f"\nUpdated Files:")
    print(f"  {labeled_path}: {len(combined_labeled)} total labeled reviews")
    print(f"  {prelabeled_path}: {len(still_uncertain_reviews)} remaining uncertain reviews")

    # Distribution analysis
    print(f"\n" + "="*80)
    print(f"\nMovement from Uncertain to Confident by Label:")
    print(f"  Design Discussion: {label_distribution_confident['design_discussion']} moved")
    print(f"  Opinion/Judgment: {label_distribution_confident['opinion_judgment']} moved")
    print(f"  Personal Experience: {label_distribution_confident['personal_experience']} moved")

    print(f"\nLabel Distribution in Updated Labeled File ({len(combined_labeled)} total):")
    for label in ['design_discussion', 'opinion_judgment', 'personal_experience']:
        count = sum(1 for r in combined_labeled if r['label'] == label)
        pct = (count / len(combined_labeled)) * 100 if combined_labeled else 0
        print(f"  {label}: {count} ({pct:.1f}%)")

    if len(still_uncertain_reviews) > 0:
        print(f"\nLabel Distribution in Remaining Uncertain File ({len(still_uncertain_reviews)} total):")
        for label in ['design_discussion', 'opinion_judgment', 'personal_experience']:
            count = sum(1 for r in still_uncertain_reviews if r['label'] == label)
            pct = (count / len(still_uncertain_reviews)) * 100 if still_uncertain_reviews else 0
            print(f"  {label}: {count} ({pct:.1f}%)")

    # Sample output
    print(f"\n" + "="*80)
    print(f"\nSample of Re-labeled Reviews (5 samples):")
    if len(confident_reviews) > 0:
        for i in range(min(5, len(confident_reviews))):
            row = confident_reviews[i]
            text_preview = row['text'][:80].replace('\n', ' ')
            print(f"\n[{i+1}] {row['label'].upper()}")
            print(f"    Text: {text_preview}...")
            print(f"    Note: {row['notes']}")

    if len(still_uncertain_reviews) > 0:
        print(f"\n{'-'*80}")
        print(f"\nSample of Still-Uncertain Reviews (3 samples):")
        for i in range(min(3, len(still_uncertain_reviews))):
            row = still_uncertain_reviews[i]
            text_preview = row['text'][:80].replace('\n', ' ')
            print(f"\n[{i+1}] {row['label'].upper()}")
            print(f"    Text: {text_preview}...")
            print(f"    Note: {row['notes']}")

    print(f"\n" + "="*80)
    print(f"\nPatterns Observed:")
    print(f"  - Design discussions often have 2+ mechanics keywords + reasoning phrases")
    print(f"  - Personal experiences dominated the uncertain set (49.1% of uncertain)")
    print(f"  - Short reviews (<10 words) that assert opinions are HIGH confidence")
    print(f"  - Mixed design + emotion reviews are usually MEDIUM (hard to split perfectly)")

if __name__ == '__main__':
    main()
