import urllib.request
import json
import datetime
from collections import defaultdict

API_KEY = "23f07e8f25d48522ffb1dbdda3bbca7b"
BASE_URL = "https://api.the-odds-api.com/v4"

today_str = "2026-10-19"
tomorrow_str = "2026-10-20"

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return None

sports_data = fetch_json(f"{BASE_URL}/sports/?apiKey={API_KEY}")
if not sports_data:
    print("Failed to fetch sports list.")
    exit(1)

active_keys = [s['key'] for s in sports_data if s.get('active')]
print(f"Found {len(active_keys)} active sports.")

matches_today = []

for s_key in active_keys:
    url = f"{BASE_URL}/sports/{s_key}/odds/?apiKey={API_KEY}&regions=eu,us,uk&markets=h2h&oddsFormat=decimal"
    data = fetch_json(url)
    if not data:
        continue
    
    for event in data:
        commence = event.get('commence_time', '')
        if commence.startswith(today_str):
            home = event.get('home_team')
            away = event.get('away_team')
            sport_title = event.get('sport_title')
            
            outcomes_prices = defaultdict(list)
            outcomes_probs = defaultdict(list)
            
            for bm in event.get('bookmakers', []):
                for mkt in bm.get('markets', []):
                    if mkt.get('key') == 'h2h':
                        outs = mkt.get('outcomes', [])
                        inv_sum = sum(1.0 / o['price'] for o in outs if o.get('price', 0) > 0)
                        if inv_sum > 0:
                            for o in outs:
                                price = o.get('price', 0)
                                if price > 0:
                                    outcomes_prices[o['name']].append(price)
                                    outcomes_probs[o['name']].append((1.0 / price) / inv_sum)
            
            if outcomes_prices:
                avg_prices = {k: sum(v)/len(v) for k, v in outcomes_prices.items()}
                avg_probs = {k: sum(v)/len(v) for k, v in outcomes_probs.items()}
                matches_today.append({
                    'sport': sport_title,
                    'key': s_key,
                    'home': home,
                    'away': away,
                    'commence': commence,
                    'avg_prices': avg_prices,
                    'avg_probs': avg_probs
                })

print(f"Total matches scheduled for today ({today_str}): {len(matches_today)}")

picks_80 = []

for m in matches_today:
    home = m['home']
    away = m['away']
    avg_p = m['avg_probs']
    avg_o = m['avg_prices']
    has_draw = "Draw" in avg_p
    
    for team, p in avg_p.items():
        if team != "Draw" and p >= 0.80:
            picks_80.append({
                'match': f"{home} vs {away}",
                'sport': m['sport'],
                'commence': m['commence'],
                'market': 'Match Winner',
                'pick': f"{team} to Win",
                'odds': round(avg_o[team], 2),
                'safety_pct': round(p * 100, 1),
                'type': 'Straight Win'
            })
            
    if has_draw:
        p_home = avg_p.get(home, 0)
        p_away = avg_p.get(away, 0)
        p_draw = avg_p.get('Draw', 0)
        
        p_1x = p_home + p_draw
        if p_1x >= 0.80:
            fair_odds = round(1.0 / p_1x, 2) if p_1x > 0 else 1.0
            est_odds = max(1.03, round(fair_odds * 0.98, 2))
            picks_80.append({
                'match': f"{home} vs {away}",
                'sport': m['sport'],
                'commence': m['commence'],
                'market': 'Double Chance',
                'pick': f"{home} or Draw (1X)",
                'odds': est_odds,
                'safety_pct': round(p_1x * 100, 1),
                'type': 'Double Chance (1X)'
            })
            
        p_x2 = p_away + p_draw
        if p_x2 >= 0.80:
            fair_odds = round(1.0 / p_x2, 2) if p_x2 > 0 else 1.0
            est_odds = max(1.03, round(fair_odds * 0.98, 2))
            picks_80.append({
                'match': f"{home} vs {away}",
                'sport': m['sport'],
                'commence': m['commence'],
                'market': 'Double Chance',
                'pick': f"{away} or Draw (X2)",
                'odds': est_odds,
                'safety_pct': round(p_x2 * 100, 1),
                'type': 'Double Chance (X2)'
            })

picks_80.sort(key=lambda x: x['safety_pct'], reverse=True)

with open("rollover_picks_today.json", "w", encoding="utf-8") as f:
    json.dump(picks_80, f, indent=2)

print(f"\nFound {len(picks_80)} picks with >= 80% safety for today!")
for p in picks_80[:20]:
    print(f"[{p['safety_pct']}%] {p['match']} | {p['pick']} @ {p['odds']} ({p['commence'][11:16]} UTC) - {p['sport']}")
