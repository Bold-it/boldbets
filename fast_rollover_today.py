import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

API_KEY = "23f07e8f25d48522ffb1dbdda3bbca7b"
BASE_URL = "https://api.the-odds-api.com/v4"
today_str = "2026-10-19"

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

sports_data = fetch_url(f"{BASE_URL}/sports/?apiKey={API_KEY}")
if not sports_data:
    print("Could not fetch sports")
    exit(1)

# Filter out outright futures / winners
h2h_sports = [
    s['key'] for s in sports_data 
    if s.get('active') and not any(w in s['key'] for w in ['_winner', '_championship', '_bowl', '_series', '_cup_winner'])
]

print(f"Scanning {len(h2h_sports)} active head-to-head leagues...")

def fetch_odds_for_sport(s_key):
    url = f"{BASE_URL}/sports/{s_key}/odds/?apiKey={API_KEY}&regions=eu,us,uk&markets=h2h&oddsFormat=decimal"
    data = fetch_url(url)
    if not data or not isinstance(data, list):
        return []
    return data

all_events = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(fetch_odds_for_sport, h2h_sports)
    for res in results:
        all_events.extend(res)

print(f"Total events retrieved: {len(all_events)}")

# Filter events for today (2026-10-19)
today_events = [e for e in all_events if e.get('commence_time', '').startswith(today_str)]
print(f"Events playing today ({today_str}): {len(today_events)}")

picks = []

for ev in today_events:
    home = ev.get('home_team')
    away = ev.get('away_team')
    sport = ev.get('sport_title', ev.get('sport_key'))
    commence = ev.get('commence_time')
    
    outcomes_prices = defaultdict(list)
    outcomes_probs = defaultdict(list)
    
    for bm in ev.get('bookmakers', []):
        for mkt in bm.get('markets', []):
            if mkt.get('key') == 'h2h':
                outs = mkt.get('outcomes', [])
                inv_sum = sum(1.0 / o['price'] for o in outs if o.get('price', 0) > 0)
                if inv_sum > 0:
                    for o in outs:
                        p = o.get('price', 0)
                        if p > 0:
                            outcomes_prices[o['name']].append(p)
                            outcomes_probs[o['name']].append((1.0 / p) / inv_sum)
                            
    if not outcomes_prices:
        continue
        
    avg_prices = {k: sum(v)/len(v) for k, v in outcomes_prices.items()}
    avg_probs = {k: sum(v)/len(v) for k, v in outcomes_probs.items()}
    has_draw = "Draw" in avg_probs
    
    # 1. Straight Win >= 0.75
    for team, p in avg_probs.items():
        if team != "Draw" and p >= 0.75:
            picks.append({
                'match': f"{home} vs {away}",
                'sport': sport,
                'commence': commence,
                'market': 'Match Winner',
                'pick': f"{team} to Win",
                'odds': round(avg_prices[team], 2),
                'safety_pct': round(p * 100, 1),
                'type': 'Straight Win'
            })
            
    # 2. Double Chance >= 0.80
    if has_draw:
        p_h = avg_probs.get(home, 0)
        p_a = avg_probs.get(away, 0)
        p_d = avg_probs.get('Draw', 0)
        
        # 1X
        p_1x = p_h + p_d
        if p_1x >= 0.80:
            fair_odds = round(1.0 / p_1x, 2) if p_1x > 0 else 1.0
            est_odds = max(1.03, round(fair_odds * 0.98, 2))
            picks.append({
                'match': f"{home} vs {away}",
                'sport': sport,
                'commence': commence,
                'market': 'Double Chance',
                'pick': f"{home} or Draw (1X)",
                'odds': est_odds,
                'safety_pct': round(p_1x * 100, 1),
                'type': 'Double Chance'
            })
            
        # X2
        p_x2 = p_a + p_d
        if p_x2 >= 0.80:
            fair_odds = round(1.0 / p_x2, 2) if p_x2 > 0 else 1.0
            est_odds = max(1.03, round(fair_odds * 0.98, 2))
            picks.append({
                'match': f"{home} vs {away}",
                'sport': sport,
                'commence': commence,
                'market': 'Double Chance',
                'pick': f"{away} or Draw (X2)",
                'odds': est_odds,
                'safety_pct': round(p_x2 * 100, 1),
                'type': 'Double Chance'
            })

picks.sort(key=lambda x: x['safety_pct'], reverse=True)

with open("c:/Users/BOLD/OneDrive/Desktop/boldbets/rollover_today.json", "w", encoding="utf-8") as f:
    json.dump(picks, f, indent=2)

print(f"\nSUCCESS: Extracted {len(picks)} high-safety picks for today (19 Oct 2026)!")
for p in picks:
    print(f"[{p['safety_pct']}%] {p['match']} | {p['pick']} @ {p['odds']} | {p['commence'][11:16]} UTC | {p['sport']}")
