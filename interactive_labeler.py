#!/usr/bin/env python3
"""
Interactive CLI tool to label uncertain reviews one at a time.
Saves progress automatically after each review.
"""

import csv
import sys
import os
from pathlib import Path

INPUT_FILE = 'data/steam_reviews_prelabeled.csv'
OUTPUT_FILE = 'data/steam_reviews_prelabeled_corrected.csv'
PROGRESS_FILE = '.labeler_progress'

# ANSI color codes
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

class Labeler:
    def __init__(self):
        self.reviews = []
        self.labeled = []
        self.current_index = 0
        self.load_reviews()
        self.load_progress()

    def load_reviews(self):
        """Load reviews from CSV"""
        if not os.path.exists(INPUT_FILE):
            print(f"{RED}❌ File not found: {INPUT_FILE}{END}")
            sys.exit(1)

        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                self.reviews.append({
                    'id': idx,
                    'text': row['text'],
                    'label': row['label'],
                    'notes': row['notes'],
                    'game': row['game']
                })

        self.labeled = [
            {**r, 'user_label': r['label'], 'user_notes': ''}
            for r in self.reviews
        ]

        print(f"{GREEN}✅ Loaded {len(self.reviews)} uncertain reviews{END}\n")

    def load_progress(self):
        """Load saved progress"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    self.current_index = int(f.read().strip())
                print(f"{CYAN}📍 Resuming from review {self.current_index + 1}{END}\n")
            except:
                self.current_index = 0

    def save_progress(self):
        """Save current progress"""
        with open(PROGRESS_FILE, 'w') as f:
            f.write(str(self.current_index))

    def format_review_text(self, text, width=80):
        """Wrap text to width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) <= width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return '\n   '.join(lines)

    def show_header(self):
        """Show separator header"""
        print(f"\n{BLUE}{'='*80}{END}")
        print(f"{BOLD}{CYAN}TakeMeter - Review Labeler{END}")
        print(f"{BLUE}{'='*80}{END}\n")

    def show_review(self):
        """Display current review"""
        if self.current_index >= len(self.reviews):
            self.show_completion()
            return False

        review = self.reviews[self.current_index]

        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        self.show_header()

        # Progress bar
        progress = self.current_index / len(self.reviews)
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        pct = int(progress * 100)
        print(f"{BOLD}Progress:{END} {bar} {pct}% ({self.current_index}/{len(self.reviews)})\n")

        # Review info
        print(f"{BOLD}Game:{END} {CYAN}{review['game']}{END}")
        print(f"{BOLD}Review #{END} {self.current_index + 1}\n")

        # Review text
        print(f"{BOLD}📝 Review:{END}")
        print(f"{YELLOW}   {self.format_review_text(review['text'], 75)}{END}\n")

        # Pre-label notes
        if review['notes']:
            print(f"{BOLD}Pre-label note:{END} {review['notes']}\n")

        # Current labels
        current = self.labeled[self.current_index]
        print(f"{BOLD}Current label:{END} {current['user_label']}")

        return True

    def show_options(self):
        """Show label options"""
        print(f"\n{BOLD}Select a label:{END}\n")
        print(f"  {BOLD}1{END}) {CYAN}📐 design_discussion{END}")
        print(f"     Discusses specific mechanics, systems, design")
        print(f"     (puzzle design, difficulty, controls, camera, etc.)\n")

        print(f"  {BOLD}2{END}) {PURPLE}💭 opinion_judgment{END}")
        print(f"     States quality without explaining why")
        print(f"     (good/bad/great/terrible without reasoning)\n")

        print(f"  {BOLD}3{END}) {CYAN}❤️  personal_experience{END}")
        print(f"     Focuses on emotional journey or feelings")
        print(f"     (scared, fun, enjoyed, personal story)\n")

        print(f"  {BOLD}n{END}) Skip to next")
        print(f"  {BOLD}p{END}) Go to previous")
        print(f"  {BOLD}q{END}) Quit\n")

    def get_label_input(self):
        """Get label choice from user"""
        label_map = {
            '1': 'design_discussion',
            '2': 'opinion_judgment',
            '3': 'personal_experience',
        }

        while True:
            choice = input(f"{BOLD}Enter choice (1-3, n, p, q):{END} ").strip().lower()

            if choice in label_map:
                return label_map[choice]
            elif choice == 'n':
                return 'next'
            elif choice == 'p':
                return 'previous'
            elif choice == 'q':
                self.quit_labeling()
            else:
                print(f"{RED}Invalid choice. Try again.{END}")

    def get_notes_input(self):
        """Get optional notes"""
        notes = input(f"\n{BOLD}Add notes (optional, press Enter to skip):{END} ").strip()
        return notes

    def next_review(self):
        """Move to next review"""
        label = self.get_label_input()

        if label == 'next':
            return self.move_next()
        elif label == 'previous':
            return self.move_previous()

        # Get notes
        notes = self.get_notes_input()

        # Save label
        self.labeled[self.current_index]['user_label'] = label
        self.labeled[self.current_index]['user_notes'] = notes

        # Save to file
        self.save_labeled_reviews()
        self.save_progress()

        print(f"\n{GREEN}✅ Saved: {label}{END}")
        input(f"{BOLD}Press Enter to continue...{END}")

        return self.move_next()

    def move_next(self):
        """Move to next review"""
        if self.current_index < len(self.reviews) - 1:
            self.current_index += 1
            self.save_progress()
            return True
        elif self.current_index == len(self.reviews) - 1:
            self.current_index += 1
            return True
        return False

    def move_previous(self):
        """Move to previous review"""
        if self.current_index > 0:
            self.current_index -= 1
            self.save_progress()
            return True
        return False

    def save_labeled_reviews(self):
        """Save labeled reviews to CSV"""
        reviews_to_save = [
            {
                'text': item['text'],
                'label': item['user_label'],
                'notes': item['user_notes'],
                'game': item['game']
            }
            for item in self.labeled[:self.current_index + 1]
        ]

        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'label', 'notes', 'game'])
            writer.writeheader()
            writer.writerows(reviews_to_save)

    def show_completion(self):
        """Show completion message"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.show_header()

        print(f"{GREEN}{BOLD}✅ All {len(self.reviews)} reviews labeled!{END}\n")

        # Final summary
        labels = {}
        for item in self.labeled:
            label = item['user_label']
            labels[label] = labels.get(label, 0) + 1

        print(f"{BOLD}Label distribution:{END}\n")
        for label, count in sorted(labels.items()):
            pct = (count / len(self.reviews)) * 100
            bar = '█' * int(pct / 5)
            print(f"  {CYAN}{label:25s}{END} {bar:20s} {count:3d} ({pct:5.1f}%)")

        print(f"\n{BOLD}Next steps:{END}")
        print(f"  1. Run: {CYAN}python3 combine_datasets.py{END}")
        print(f"  2. This will create: {CYAN}data/steam_reviews_final.csv{END}")
        print(f"  3. Ready for M4 (fine-tuning)!\n")

        # Save final file
        self.save_labeled_reviews()
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)

    def quit_labeling(self):
        """Quit labeler"""
        print(f"\n{YELLOW}Saved progress - you can resume later!{END}\n")
        sys.exit(0)

    def run(self):
        """Main loop"""
        while self.show_review():
            self.show_options()
            self.next_review()

        self.show_completion()

def main():
    try:
        labeler = Labeler()
        labeler.run()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interrupted - progress saved!{END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{END}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
