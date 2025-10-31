from bs4 import BeautifulSoup
import requests


def get_ufc_odds(event_id):
    ufc_url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{event_id}.json"
    return requests.get(ufc_url).text


def get_best_fight_odds():
    url = "https://www.bestfightodds.com/#"
    result = requests.get(url).text

    doc = BeautifulSoup(result, "html.parser")
    tbody = doc.find_all("tbody")[1]
    trs = tbody.contents
    skip = ["▲", "▼", ""]

    fights = list()

    id = -1
    for tr in trs:
        spans = tr.find_all("span")  # type: ignore
        if len(spans) == 0:
            continue
        id += 1
        fighter = spans[0].text
        bets = [abs(int(span.text)) for span in spans[1:] if span.text not in skip]
        if len(bets) == 0:
            bet = None
        else:
            bet = max(bets)
        if id % 2 == 0:
            fight = {}
            if not fight.get("fighters"):
                fight["fighters"] = [fighter]
            else:
                fight["fighters"].append(fighter)
            fight[fighter] = bet
            fights.append(fight)
        else:
            fight = fights[id // 2]
            if not fight.get("fighters"):
                fight["fighters"] = [fighter]
            else:
                fight["fighters"].append(fighter)
            fight[fighter] = bet
            fights[id // 2] = fight

    return fights
