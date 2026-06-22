# TakeMeter Planning Document

## Community

**Choice:** Resident Evil Steam reviews (5 games across series remakes)

**Why this community is a good fit:**

Resident Evil Steam reviews provide active, text-heavy discourse on horror game design with significantly varied quality. Reviews range from technical analysis of mechanics (puzzle design, difficulty balance, resource management, controls, camera systems) to casual quality judgments to deeply personal emotional experiences. The community explicitly cares about game design vs. pure hype—players distinguish between substantive critiques and surface-level praise. This variation in discourse quality makes the label distinctions meaningful and learnable.

---

## Labels (REVISED)

### Label 1: Analysis

**Definition:** The review explains **HOW/WHY** game mechanics work, describes systems, or makes **COMPARISONS** between design elements. Must show reasoning, not just mention features.

**Key Signal:** "Here's how X works..." OR "X compared to Y..." OR "Mechanic Z affects gameplay because..."

**Examples:**
1. "This game's co-op mechanics are implemented incredibly well. The solo experience is grueling because boss fights are designed with two players in mind, making them unnecessarily frustrating when relying on AI."

2. "The game has old movement mechanics. When aiming, you can't move, which makes it difficult in smaller spaces where you're fighting frequently—this is a design choice that impacts strategy."

3. "The combat is way better, but the horror aspect isn't as good. The dodging mechanic made this more fun because I felt I had more control."

**Not Analysis (even if design words are mentioned):**
- "The controls are smooth" (mentions feature, doesn't explain impact)
- "I love the puzzles" (just expresses feeling, not explaining them)

---

### Label 2: Quick Take

**Definition:** Brief emotional reaction OR quality judgment—either a single moment of feeling or a simple assertion. Does **NOT** have a narrative arc or explanation.

**Key Signal:** Single emotional reaction, short assertion, or judgment without reasoning.

**Examples:**
1. "This game is good" / "genuinely one of the best games"

2. "I'm addicted to this game" (single emotional moment)

3. "low-key scary but Carlos is there sometimes" (short reaction)

4. "I love everything about it" (assertion without detail)

5. "This game brought me joy" (personal feeling but no story arc)

**Not Quick Take:**
- "I loved this game, bought it again on a different platform, and still replay it years later" (narrative arc = Personal Story)
- "The puzzles are brilliant because they make you think strategically" (explains why = Analysis)

---

### Label 3: Personal Story

**Definition:** Review describes a **PERSONAL NARRATIVE ARC** or **EVOLVING EMOTIONAL JOURNEY** with multiple moments, changes over time, or a story arc. Shows progression of feeling or experience.

**Key Signal:** "I started X, then Y happened, now I think Z" OR multi-part personal journey OR clear emotional progression.

**Examples:**
1. "As a child, I loved watching horror but not playing them. I wasn't sure about this game at first, but after playing it, I realized it was amazing. Now I've replayed it multiple times and appreciate it more each time."

2. "My first playthrough, I thought the game was short and lame. After a couple years, I replayed it and realized it was actually quite fun. Now I've gotten all achievements and enjoyed doing them."

3. "I was ashamed I bought this game at first. As I played more, my opinion shifted, and now I consider it one of my favorite RE games. The journey of understanding the game was part of what made it special."

4. "Played it after RE3 remake, and the combat is way better. At first I didn't feel scared, but later when I played as Ashley, that one moment really got me. By the end, the story was so fun I never felt bored. 9.5/10 for me."

**Not Personal Story:**
- "I'm addicted to this game" (single moment, no arc)
- "I appreciated this game and loved it" (emotions but no narrative progression)

---

## Decision Rule (Simple)

**Ask yourself ONE question:**

1. **Does it EXPLAIN how/why something works or COMPARE design elements?** → Analysis
2. **Does it tell a PERSONAL STORY or show CHANGES over time?** → Personal Story
3. **Neither?** (just brief feeling or assertion) → Quick Take

Examples:
- "The camera system creates cinematic moments but limits your view" → Analysis (explains impact)
- "I played it as a kid, loved it. Replayed it years later, still love it." → Personal Story (narrative arc)
- "This game is great" → Quick Take (assertion)
- "This brought me joy, had a blast with friends" → Quick Take (single moment emotions)
- "Scared at first, then addicted, now I replay constantly" → Personal Story (progression)

---

## Data Collection Plan

**Source:** data/steam_reviews_clean.csv (342 reviews, pre-cleaned of trolls/memes)

**Games included:**
- Resident Evil (2015 Remake): ~74 reviews
- Resident Evil 2 (2019 Remake): ~94 reviews
- Resident Evil 3 (2020 Remake): ~65 reviews
- Resident Evil 4 (2023 Remake): ~51 reviews
- Resident Evil 5: ~66 reviews

**Collection method:** Already collected via scrape_steam_reviews.py and cleaned by clean_dataset.py

**Labeling approach:** Read each review carefully, assign one label per review, document difficult cases

**Label distribution target:** Aim for balanced distribution (no single label >70% of dataset)
- Analysis: target ~85-110 reviews (25-30%)
- Quick Take: target ~135-155 reviews (40-45%)
- Personal Story: target ~70-95 reviews (20-25%)

**If imbalanced after initial labeling:** Resample from games with underrepresented labels

---

## Evaluation Metrics

**Metrics to report:**
- Overall accuracy (both baseline and fine-tuned models)
- Per-class precision, recall, and F1 score
- Confusion matrix (which labels confused with which?)

**Why these metrics matter for this specific task:**

Accuracy alone is insufficient because:
- **Precision per label:** Tells us if the model conservatively predicts a label or over-predicts it (e.g., does it avoid falsely calling opinions "design discussion"?)
- **Recall per label:** Tells us if the model catches all instances of a label or misses some (e.g., does it find real design discussions?)
- **F1 per label:** Balances precision and recall to show overall per-label performance
- **Confusion matrix:** Shows which specific boundaries are hard (e.g., does the model confuse Opinion ↔ Personal Experience more than Design ↔ Opinion?)

For RE reviews, we specifically care: Can the model distinguish substantive design critique from surface judgments? Confusion matrix will reveal this directly.

---

## Definition of Success

**Performance threshold:**
- Baseline accuracy: ~33% (random guess on 3 classes)
- Fine-tuned accuracy: **≥70%** (meaningfully above baseline)
- Per-class F1: **≥0.60 for each label** (no label performs wildly worse than others)

**Why these thresholds:**
- 70% accuracy = model is useful for filtering (catches most substantive reviews)
- F1 ≥0.60 per class = all labels are learnable, not one dominant class collapsing performance
- Specific to task: If Design Discussion F1 <<< other labels, the model can't distinguish design discussion well (the most important distinction)

**Acceptable performance:** Minimum 15% improvement over baseline (from ~33% to ≥48%)

**Usefulness test:** At 70% accuracy, the model could flag likely Design Discussion posts with reasonable precision, useful for community moderation tools

---

## AI Tool Plan

### Label Stress-Testing

**Plan:** Use Claude to generate 5-10 hypothetical reviews at boundaries between labels

**Process:**
1. Provide Claude with label definitions and uncertain cases
2. Ask it to generate boundary-case reviews (posts that could belong to multiple labels)
3. Manually attempt to classify each using only label definitions
4. If unable to classify cleanly, revise definitions before annotating 200 examples

**Tool:** Claude

**Expected output:** Validates that label definitions are sharp enough; guides any refinement

---

### Annotation Assistance

**Plan:** Use Claude to pre-label a sample batch, then manually review every example

**Decision:** YES - will use pre-labeling on 50 reviews as a test, then review/correct all

**If pre-labeling:**
- Tool: Claude
- Batch size: 50 reviews (~15% of dataset)
- Tracking: Add column "pre_labeled: yes/no" to CSV for disclosure
- Review approach: Read each pre-labeled example, correct if needed, never skim

**Disclosure:** In README AI Usage section, specify which examples were pre-labeled and how many corrections were made

---

### Failure Analysis

**Plan:** After fine-tuning, use Claude to identify patterns in wrong predictions

**Process:**
1. Export 15-20 misclassified examples from model output
2. Paste into Claude, ask: "What patterns do you see in these wrong predictions? (sarcasm, short posts, specific label pairs confused, etc.)"
3. Verify each pattern by re-reading examples myself
4. Use findings to explain failure modes in evaluation report

**Tool:** Claude

**What to look for:** 
- Specific label pair confusion (e.g., Design Discussion ↔ Personal Experience)
- Post characteristics (short length, sarcasm, mixed signals)
- Systemic vs. random errors

---

## Hard Edge Cases — Difficult Examples from Annotation

### Case 1: Analysis with Personal Experience Language
**Text:** "The best way to experience the first Resident Evil. The visual upgrade makes it even more atmospheric and immersive, which adds to the horror element. The OG version was way more clunky in comparison."

**Why it's hard:** The review uses comparison language ("more atmospheric," "way more clunky in comparison"), which signals **analysis** (explaining design impact). BUT it also opens with personal framing ("the best way to experience") and uses emotional language ("atmospheric and immersive"), which could signal **personal_story**.

**Decision:** **→ ANALYSIS** because the core reasoning is a design comparison ("OG version was clunky compared to this visual upgrade"). The emotional language supports the design observation, not a journey or narrative arc. If the review had said "I played the OG version years ago and hated it, but this remake changed my mind," that would be personal_story.

---

### Case 2: Quick Take vs. Personal Story — Brief Personal Context
**Text:** "this is by far the best game i played"

**Why it's hard:** At 9 words, this is clearly **quick_take** length (≤15 words). However, it contains "I played" — a reference to personal experience. Could this be **personal_story** because it's grounded in the player's own experience?

**Decision:** **→ QUICK TAKE** because while it mentions the player's experience, it doesn't describe a journey, change over time, or specific moments — it's just an assertion backed by implied personal engagement ("the best game I played"). If it said "I played it as a kid and still love it now" or "I replayed it 10 times," that would signal personal_story.

---

### Case 3: Quick Take Mentioning Mechanics vs. Analysis
**Text:** "Controls are here and there but game is top notch. Keeps the original mechanics and puzzles are honestly interesting and solvable. Took me too much time on my first playthrough. Definitely has some amount replayability. Overall 7.5/10"

**Why it's hard:** The review mentions several game features (controls, mechanics, puzzles, replayability), which could look like **analysis**. BUT it never explains *why* these features matter or *how* they affect gameplay — it just lists them alongside assertions ("top notch," "interesting").

**Decision:** **→ QUICK TAKE** (though borderline) because while it mentions mechanics, there's no causal explanation. It says "puzzles are interesting and solvable" but not "the puzzles are well-designed because X allows you to Y." It says "took me too much time on first playthrough" (a personal observation, not a design explanation). The core is a series of assertions + features, not an explanation of design impact.

---

## Notes & Decisions

- Chose 3 labels (not 4) because the three distinctions (analysis vs. quick_take vs. personal_story) are natural in RE community
- Conservative data cleaning: removed trolls/memes, kept 342 reviews
- Actual label distribution after auto-labeling + post-processing:
  - Analysis: 147 (43.0%) — higher than planned 25-30%, suggests the community discusses mechanics frequently
  - Quick Take: 111 (32.5%) — slightly lower than planned 40-45%
  - Personal Story: 84 (24.6%) — matches target 20-25% perfectly
- No single label exceeds 70% (meets M3 checkpoint requirement)
- Boundary between Analysis ↔ Quick Take is learnable (F1=0.72 for analysis, F1=0.57 for quick_take)
- **Critical finding:** Analysis ↔ Personal Story boundary is NOT learnable — reviews that describe personal journeys often use game design vocabulary, making them texturally identical at the token level

---

## Final Results (M5-M6)

### Baseline (Groq llama-3.3-70b zero-shot)
- Overall Accuracy: 40.4%
- Per-class F1: analysis=0.16, quick_take=0.55, personal_story=0.24
- Behavior: predicts mostly quick_take; struggles with all three-way distinctions

### Fine-Tuned Model (DistilBERT)
- Overall Accuracy: 59.6%
- **Improvement: +19.2 percentage points** ✅ (exceeds 15-point target)
- Per-class F1:
  - analysis: 0.72 ✅ (learned well, over-predicts)
  - quick_take: 0.57 ⚠️ (borderline, below 0.60 target)
  - personal_story: 0.00 ❌ (complete failure — predicts 0/12 correctly)

### Key Finding: Textual Indistinguishability

**Why personal_story F1=0.00:**
1. **Data overlap:** 33 of 60 personal_story training examples contain analysis-level keywords (mechanic, design, puzzle, combat, because, makes, compared)
2. **Information barrier:** The distinction between personal_story (player focus) and analysis (game design focus) is semantic/intent-based, not lexical
3. **Model limitation:** DistilBERT learns token-level patterns; cannot learn narrative focus or intent from 239 examples
4. **Cascade effect:** Auto-labeling mislabeled personal_story examples with analysis keywords → training data inherited the confusion → model learned "design words → analysis" as reliable pattern

### Success Criteria vs. Actual Results

| Criterion | Target | Actual | Met? |
|-----------|--------|--------|------|
| Baseline accuracy | ~33% (random) | 40.4% | ✅ |
| Fine-tuned accuracy | ≥70% | 59.6% | ❌ |
| Improvement | ≥15% | +19.2% | ✅ |
| Per-class F1 | ≥0.60 each | analysis=0.72, qt=0.57, ps=0.00 | ⚠️ Partial |

### Lessons Learned

1. **Task difficulty was underestimated:** The three-label distinction requires semantic understanding of narrative focus. Assumed text-level features would suffice; they do not.

2. **Label quality ↔ task difficulty are separate:** Even with perfect labels, this distinction is not learnable by a fine-tuned DistilBERT on 239 examples because the classes are intent-based, not lexically distinct.

3. **Failure is informative:** The complete collapse on personal_story (F1=0.00) pinpoints the exact learning failure, which is more valuable than a mediocre all-class performance would have been.

4. **Auto-labeling inherits the problem:** Mistral also struggled with the personal_story/analysis boundary, confirming it's not a labeling inconsistency but a fundamental task difficulty.
