# TakeMeter Planning Document

## Community

**Choice:** Resident Evil Steam reviews (5 games across series remakes)

**Why this community is a good fit:**

Resident Evil Steam reviews provide active, text-heavy discourse on horror game design with significantly varied quality. Reviews range from technical analysis of mechanics (puzzle design, difficulty balance, resource management, controls, camera systems) to casual quality judgments to deeply personal emotional experiences. The community explicitly cares about game design vs. pure hype—players distinguish between substantive critiques and surface-level praise. This variation in discourse quality makes the label distinctions meaningful and learnable.

---

## Labels

### Label 1: Design Discussion

**Definition:** The review discusses specific game mechanics, level design, puzzle design, difficulty balance, visual/audio design, control systems, or pacing choices with concrete observations about how those systems work.

**Examples:**
1. "The Spencer Mansion is paced expertly... Resource management matters, exploration is rewarding, and solving puzzles feels genuinely satisfying. The fixed camera angles add so much atmosphere and cinematic quality to every room. The new Crimson Heads mechanic creates a lot of tension when choosing which zombies to kill..."

2. "The game has old movement mechanics... Found it frustrating to move quickly away from enemies at times even towards the end of the game. When your aiming down sight, reloading or using an item you can't move, which can make it difficult in the smaller places that you will be fighting in often."

**Uncertain case:** "The atmosphere in the RPD is incredible, the resource management actually makes you think, and the tension never lets up. Every bullet feels like it matters, every save room feels like a tiny relief before the next nightmare."
→ Why uncertain: Blends design observation (resource management, tension mechanic) with emotional effect (how it makes player feel). Resolution: If explaining HOW mechanic works technically → Design Discussion. If describing emotional EFFECT → Personal Experience. This emphasizes emotional effect despite mentioning mechanics → Personal Experience (borderline).

---

### Label 2: Opinion/Judgment

**Definition:** The review states an overall quality assessment (good/bad/great/overrated/terrible) without explaining why through specific mechanics, design observations, or evidence.

**Examples:**
1. "this game is the best and chris redfield is da man"

2. "This game is beautiful, I love everything about it"

3. "I don't like this game. That's it."

**Uncertain case:** "The perfect remake. genuinely. it's everything from the original but better."
→ Why uncertain: Asserts judgment ("perfect", "better") but doesn't explain HOW/WHY. Resolution: If only ASSERTS without explanation → Opinion. If explains WHAT made it better → Design Discussion. This asserts without explanation → Opinion/Judgment.

---

### Label 3: Personal Experience

**Definition:** The review focuses on the player's emotional journey, sensory reaction, personal feelings, or how the game made them feel during gameplay.

**Examples:**
1. "I got this game because I was stuck playing the same few games over and over again and I needed something new and fun, and this game was absolutely perfect for that. It was fun and gave me a good scare, and the puzzles were super fun to solve. The mansion was huge and fun to explore, and backtracking didn't really feel too much like a chore. My favorite part bar none was seeing the story unfold throughout the game through the notes left behind."

2. "This game made me scared of windows"

3. "Anybody who hates this game doesn't have friends. Playing with my friend screaming at each other's ears for hours on end till the next day was a once in a lifetime experience, and we quote Wesker every time we talk now."

**Uncertain case:** "I went for the Platinum achievement, and every playthrough showed me something new. It never stopped being fun! I loved how it all started, the journey of Chris and Jill as the early main cast of RE."
→ Why uncertain: Describes personal journey ("loved", "fun", "playthrough") but implies game design feature (replayability). Resolution: If describing PLAYER'S EXPERIENCE/EMOTIONS → Personal Experience. If explaining GAME FEATURES that enabled it → Design Discussion. This is about player's journey → Personal Experience.

---

## Hard Edge Cases & Decision Rules

**Cross-label ambiguity (most challenging):**

Post: *"it's not a perfect game, far from it. It's incredibly janky and the gameplay and story goes haywire, but I still love it for how as it is. Playing with my friend for the whole day screaming at each other's ears for hours on end till the next day was a once in a lifetime experience, and we quote Wesker every time we talk now. Over 100 hours invested."*

Could be: Design Discussion (mentions "janky gameplay"), Opinion (states "not perfect", "love it"), or Personal Experience (describes shared friend experience, emotional memories)

**Decision Rule:** 
- If review focuses on WHAT ASPECTS of the game work/don't work → Design Discussion
- If review focuses on PERSONAL EMOTIONAL JOURNEY/FEELINGS → Personal Experience  
- If review primarily ASSERTS QUALITY JUDGMENT → Opinion/Judgment

In this case: Core is the emotional experience ("once in a lifetime", "quote Wesker every time we talk"), with gameplay issues mentioned as context → **Personal Experience**

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
- Design Discussion: target ~85-110 reviews (25-30%)
- Opinion/Judgment: target ~135-155 reviews (40-45%)
- Personal Experience: target ~70-95 reviews (20-25%)

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

## Notes & Decisions

- Chose 3 labels (not 4) because the three distinctions (what vs. how you feel vs. judgment) are natural in RE community
- Conservative data cleaning: removed 8 trolls/memes, kept 342 reviews (~97%)
- Balanced label distribution expected: ~25% Design, ~40% Opinion, ~25% Experience
- Cross-game data: will note in evaluation if certain games are harder to label than others
