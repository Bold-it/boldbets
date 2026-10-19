# BoldBets — Prediction Engine Logic
## Super Duo | Correct Score | Super Accumulator

---

## 🧠 Core Philosophy: "Safety First" Scoring System

Every prediction must pass through a **Confidence Score (CS)** — a number from 0–100.
Only predictions above a threshold are shown to the user:
- Super Duo: CS ≥ 70
- Correct Score: CS ≥ 60
- Super Accumulator: CS ≥ 75 (per leg) and combined probability ≥ 20%

---

## 📦 Data Inputs (From Our APIs)

| Data Point | Source | Used For |
|---|---|---|
| Pre-match odds (Home/Draw/Away) | The Odds API | Implied probability |
| Over/Under 2.5 odds | The Odds API | Goals prediction |
| Both Teams to Score odds | The Odds API | Correct score filter |
| Team form (last 5-10 matches) | API-Sports | Form weight |
| Head-to-head history | API-Sports | Pattern recognition |
| Goals scored/conceded avg | API-Sports | Poisson model input |
| Home/Away split stats | API-Sports | Venue adjustment |
| Injuries / suspensions | API-Sports | Risk deduction |
| League average goals/game | API-Sports | Poisson λ calibration |

---

## 🔢 Step 1 — Implied Probability from Odds

Convert raw bookmaker odds → True Probability (remove vig/margin):

```
Raw Probability = 1 / decimal_odds

# For a 3-way market (H/D/A):
margin = (1/H_odds) + (1/D_odds) + (1/A_odds)   # typically 1.05–1.10

True P(Home) = (1/H_odds) / margin
True P(Draw) = (1/D_odds) / margin
True P(Away) = (1/A_odds) / margin
```

➡️ Use **consensus odds** (average across 3–5 bookmakers) to reduce single-book bias.

---

## 📊 Step 2 — Poisson Goal Model

Poisson distribution models the number of goals scored independently by each team.

### Inputs:
- `attack_strength_home` = (Home team avg goals scored at home) / (League avg goals scored at home)
- `defense_weakness_home` = (Home team avg goals conceded at home) / (League avg goals conceded at home)
- `attack_strength_away` = (Away team avg goals scored away) / (League avg goals scored away)
- `defense_weakness_away` = (Away team avg goals conceded away) / (League avg goals conceded away)
- `league_avg_home_goals` = avg home goals across entire league
- `league_avg_away_goals` = avg away goals across entire league

### Expected Goals (λ):
```
λ_home = attack_strength_home × defense_weakness_away × league_avg_home_goals
λ_away = attack_strength_away × defense_weakness_home × league_avg_away_goals
```

### Score Probability Matrix:
For each scoreline (H:A) where H = 0..5, A = 0..5:
```
P(H goals = h) = (e^-λ_home × λ_home^h) / h!
P(A goals = a) = (e^-λ_away × λ_away^a) / a!
P(Score = h:a) = P(H=h) × P(A=a)
```

This gives a 6×6 matrix (36 possible scorelines) with probabilities.

### Aggregate Outcomes:
```
P(Home Win) = sum of P(h:a) where h > a
P(Draw)     = sum of P(h:a) where h = a
P(Away Win) = sum of P(h:a) where h < a
```

---

## Step 3 — Form & Context Adjustments

Apply weighted multipliers to λ_home and λ_away:

| Factor | Adjustment Rule |
|---|---|
| **Recent Form** | Win=+3pts, Draw=+1pt, Loss=0pt over last 5 games. Scale: (pts/15). Apply as ±10% to attack λ |
| **H2H Record** | If team dominates H2H (≥60% wins), boost their attack λ by +5% |
| **Key Injury** | If striker missing → reduce attack λ by 10–15%. If goalkeeper → reduce defense by 10% |
| **Home advantage** | Already baked into λ_home using home-specific stats |
| **Rest days** | < 3 days rest → reduce λ by 8% (fatigue penalty) |
| **Motivation** | Relegation battle / title race → boost λ by 5% for motivated side |

---

## 🥇 SUPER DUO Logic

**Definition:** A 2-selection bet where BOTH must win. Target: HIGH confidence, LOW risk doubles.

### Selection Algorithm:
1. Run Poisson + form model for ALL available matches.
2. Filter matches where:
   - `True P(outcome) ≥ 0.60` (60%+ probability for chosen outcome)
   - Odds for that outcome are between `1.30 – 2.20` (value zone, not too short)
   - No key injuries on predicted winning side
   - Last 5 form: team has ≥ 3 wins
3. Rank by **Value Score**:
   ```
   Value = True_Probability × Decimal_Odds
   # If Value > 1.0 → the bet has positive expected value (+EV)
   ```
4. Pick TOP 2 matches by Value Score.
5. Combine: `Combined_Odds = Odds_1 × Odds_2`
6. Combined Probability = `P_1 × P_2`
7. Only publish if Combined_P ≥ 0.40 (40%+)

### Output Example:
```
Super Duo:
  Leg 1: Man City vs Arsenal → Man City Win @ 1.65 (P=63%)
  Leg 2: PSG vs Lyon → Over 2.5 Goals @ 1.75 (P=59%)
  Combined Odds: 2.89 | Combined P: 37% | Confidence: 72/100
```

---

## 🎯 CORRECT SCORE Logic

**Definition:** Predict exact final score. High difficulty, but systematic approach reduces guesswork.

### Step-by-Step:

**Phase 1 — Build Score Probability Matrix**
Use Poisson model to generate all P(h:a) for h,a ∈ {0,1,2,3,4,5+}

**Phase 2 — Filter Viable Scores**
Only consider scores where:
- `P(h:a) ≥ 0.08` (at least 8% raw probability — avoids wild guesses)
- Bookmaker odds for the score are ≤ 15.0 (eliminate extreme longshots)
- Score is consistent with O/U 2.5 market (e.g., if O2.5 is favored, don't pick 0-0 or 1-0)

**Phase 3 — Cross-validate with O/U & BTTS**
```
If P(Over 2.5) > 0.55:
   Focus on scores: 2-1, 1-2, 2-0, 0-2, 3-1, 1-3, 2-2
If P(BTTS=YES) > 0.60:
   Eliminate scores where one team scores 0 (0-1, 1-0, 0-0, etc.)
If P(Home Win) > 0.55 AND P(Over 2.5) > 0.55:
   Top candidates: 2-1, 2-0, 3-1
```

**Phase 4 — Score Cluster Pick**
Present TOP 3 most probable valid scores as "banker" and "alternatives":
```
Correct Score Prediction:
  🏆 Banker: 2-1 Home Win  (P=14.2%, Odds ~6.5)
  📌 Alt 1:  1-1 Draw      (P=11.8%, Odds ~5.8)
  📌 Alt 2:  2-0 Home Win  (P=10.4%, Odds ~7.0)
```

**Phase 5 — Confidence Score for Correct Score**
```
CS_correct_score = (Poisson_P × 0.5) + (Odds_alignment × 0.3) + (H2H_pattern × 0.2)
# Odds alignment = how close our Poisson prob is to what bookmaker implies
# H2H pattern = % of past H2H matches that ended with this scoreline type
```

---

## 🚀 SUPER ACCUMULATOR Logic

**Definition:** A multi-leg accumulator (5–10 selections) designed to maximize returns while maintaining systematic safety.

### The Problem:
Each added leg MULTIPLIES risk. A 8-leg acca with avg 60% chance per leg:
`0.60^8 = 1.7%` — terrible. We need smarter leg selection.

### Solution — The 3-Tier Confidence Filter:

**Tier 1 — Anchor Legs (MUST include, CS ≥ 80)**
- Heavy favorites with strong form, clean H2H, no injuries
- Odds: 1.20 – 1.55
- These are "banker" legs — very likely to land

**Tier 2 — Value Legs (CS 70–79)**
- Good probability but slightly higher odds (1.55 – 2.10)
- Add 2–3 of these for multiplier boost

**Tier 3 — Wildcard Legs (CS 60–69, max 1–2)**
- Slightly riskier but high value — odds 2.10 – 3.00
- Max 2 wildcards allowed in any accumulator

### Accumulator Construction Algorithm:
```
1. Run model on ALL available matches (same day / next 48h)
2. Tag each selection as Tier 1 / 2 / 3 based on CS
3. Build accumulator:
   - Minimum 2 × Tier 1 (anchors)
   - 2–3 × Tier 2 (value)
   - 0–2 × Tier 3 (wildcards, optional)
   - Total legs: 5–8
4. Calculate:
   Combined_P = P_1 × P_2 × ... × P_n
   Combined_Odds = O_1 × O_2 × ... × O_n
5. Safety Gate: only publish if Combined_P ≥ 0.15 (15%)
6. Display ROI expectation:
   Expected_Value = Combined_P × Combined_Odds
   # If EV > 1.2 → Green light ✅
   # If EV 1.0–1.2 → Yellow, borderline ⚠️
   # If EV < 1.0 → Reject ❌
```

### Anti-Correlation Rule:
```
Never combine two legs from the SAME match
(e.g., "Man City Win" + "Over 2.5 in Man City match" are correlated)
Exception: allowed ONLY if it's a Correct Score acca where the score implies both
```

### Output Example:
```
🚀 SUPER ACCUMULATOR (6 legs)
---
Leg 1 [🔒 Anchor]: Bayern Munich Win @ 1.30 (CS: 88) P=77%
Leg 2 [🔒 Anchor]: Liverpool Win @ 1.45 (CS: 82) P=69%
Leg 3 [💎 Value]:  Over 2.5 — Real Madrid vs Atletico @ 1.80 (CS: 74) P=61%
Leg 4 [💎 Value]:  Inter Milan Win @ 1.70 (CS: 71) P=64%
Leg 5 [💎 Value]:  BTTS YES — Arsenal vs Chelsea @ 1.75 (CS: 70) P=62%
Leg 6 [🎲 Wild]:   Surprise: Brentford Win vs West Ham @ 2.50 (CS: 63) P=52%
---
Combined Odds:  27.9×
Combined P:     13.1%
Expected Value: 3.65 ✅ (STRONG POSITIVE EV)
Confidence:     74/100
```

---

## 🔄 Overall Prediction Pipeline

```
[API Fetch: Odds + Stats]
        ↓
[Vig Removal → True Probabilities]
        ↓
[Poisson λ Calculation]
        ↓
[Form + Context Adjustments]
        ↓
[Score Matrix Generation]
        ↓
[Safety Gates Applied]
        ↓
[Super Duo] [Correct Score] [Super Acca]
        ↓
[Confidence Score Assigned]
        ↓
[Publish to UI if CS passes threshold]
```

---

## ⚠️ Risk Management Rules (Always Apply)

| Rule | Detail |
|---|---|
| **Never auto-include** | No prediction goes out without passing ALL filters |
| **Recency bias guard** | Don't weight recent form >40% — small sample size |
| **Odds sanity check** | If our model says 70% but bookie offers 2.50+ → flag as suspicious (line movement, insider info) |
| **Market movement alert** | If odds move >15% in 2h before kickoff → re-run model, may indicate team news |
| **No same-day reschedule** | Reject any match with a postponement/rescheduling flag |
| **Low liquidity filter** | Avoid obscure leagues where odds are thin and bookmakers have huge margins |
