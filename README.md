# ⚡ BoldBets — Sports Betting Pro Analysis Engine

> High-probability, data-driven sports betting analysis engine designed for disciplined daily rollovers, super duos, and accumulator optimization with **≥80% safety thresholds**.

---

## 🎯 What is BoldBets?

BoldBets removes emotional bias and bookmaker tricks by calculating **vig-removed true probabilities** across 60+ global sports leagues. Rather than chasing high-odds lotteries, BoldBets identifies statistical value and ultra-safe selections for compounding bankrolls through structured **Daily Rollover Challenges**.

### 🌟 Key Features
- **🛡️ 80%+ True Safety Filter:** Automatically filters matches across worldwide leagues where the statistical win probability exceeds 80%.
- **🚀 Automated Daily Rollover Engine:** Generates curated 1-to-2 leg rollover tickets targeting `1.20x` – `1.30x` odds for 10-day compounding cycles.
- **📊 Vig & Overround Stripper:** Normalizes bookmaker odds by removing their built-in margin to reveal true mathematical expected value.
- **🔄 Smart Double Chance Analyzer:** Synthesizes multi-outcome probabilities (1X / X2) to drastically cut risk on elite teams.
- **🌐 Global Multi-Sport Coverage:** EPL, La Liga, Serie A, Bundesliga, Champions League, Saudi Pro League, NFL, NHL, European Handball, and more.

---

## 📁 Repository Structure

```
boldbets/
├── fast_rollover_today.py       # High-speed multi-threaded odds fetcher & 80%+ engine
├── get_rollover_today.py        # Core sports analysis script
├── DAILY_ROLLOVER.md            # Rollover Challenge protocol, rules & 10-day compounding simulation
├── PREDICTION_LOGIC.md          # Deep dive into the mathematical algorithms & vig removal
├── PICKS_REPORT.md              # Detailed safety tier breakdown of today's fixtures
├── rollover_today.json          # Extracted high-safety picks for today
├── mega_all_picks.json          # Consolidated candidate pool
├── .env.example                 # Template for API keys
└── .gitignore                   # Ignores sensitive keys and cache files
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.9+
- The Odds API Key (Free tier: 500 requests/month at [the-odds-api.com](https://the-odds-api.com/))

### 2. Setup
Clone the repository:
```bash
git clone https://github.com/Bold-it/boldbets.git
cd boldbets
```

Configure your API key:
```bash
cp .env.example .env
# Edit .env and paste your API key
```

### 3. Run the Daily Rollover Engine
Fetch and scan all active global matches kicking off today:
```bash
python fast_rollover_today.py
```
Output results will be printed to terminal and saved to `rollover_today.json`.

---

## 📐 Mathematical Model Overview

Bookmaker odds include a profit margin (*overround* or *vig*):

$$\sum_{i=1}^{n} \frac{1}{\text{Odds}_i} = 1 + \text{Vig}$$

BoldBets calculates the true probability $P_{\text{true}}(i)$ for outcome $i$:

$$P_{\text{true}}(i) = \frac{\frac{1}{\text{Odds}_i}}{\sum_{j=1}^{n} \frac{1}{\text{Odds}_j}}$$

For 3-way markets (Home / Draw / Away), the Double Chance True Safety is:

$$P_{\text{true}}(1X) = P_{\text{true}}(\text{Home}) + P_{\text{true}}(\text{Draw})$$
$$P_{\text{true}}(X2) = P_{\text{true}}(\text{Away}) + P_{\text{true}}(\text{Draw})$$

Only selections where $P_{\text{true}} \ge 0.80$ qualify for the **BoldBets Rollover Challenge**.

---

## ⚖️ Disclaimer
*BoldBets is an analytical tool built for statistical probability research. Sports betting inherently carries financial risk. Practice responsible bankroll management.*
