from bs4 import BeautifulSoup
import requests
import json


def get_ufc_odds(event_id):
    ufc_url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{event_id}.json"
    return json.loads(requests.get(ufc_url).text)


def edited_ufc_odds(event_id):
    data = get_ufc_odds(event_id)
    fights = list()
    for fight in data["LiveEventDetail"]["FightCard"]:
        fights.append(trim(fight))
    new_data = dict()
    new_data["id"] = data["LiveEventDetail"]["EventId"]
    new_data["event"] = data["LiveEventDetail"]["Name"]
    new_data["date"] = data["LiveEventDetail"]["StartTime"][:10]
    new_data["fights"] = fill_odds(fights)
    return new_data


def fill_odds(fights):
    url = "https://www.bestfightodds.com/#"
    result = requests.get(url).text

    doc = BeautifulSoup(result, "html.parser")
    for tbody in doc.find_all("tbody")[1::2]:
        trs = tbody.contents

        id = -1
        for tr in trs:
            spans = tr.find_all("span")  # type: ignore
            if len(spans) == 0:
                continue
            id += 1
            name = spans[0].text
            for idx, fight in enumerate(fights):
                if fight.get(name) and fight[name] == 100:
                    fights[idx][name] = get_bet(spans)
    return fights


def get_bet(spans):
    skip = ["▲", "▼", ""]
    bets = [abs(int(span.text)) for span in spans[1:] if span.text not in skip]
    if len(bets) == 0:
        bet = 100
    else:
        bet = max(bets)
    return bet


def trim(fight):
    data = dict()
    data["id"] = fight["FightId"]
    data["date"] = fight["CardSegmentStartTime"][:10]
    data["fighters"] = [
        fight["Fighters"][0]["FighterId"],
        fight["Fighters"][1]["FighterId"],
    ]
    data[fight["Fighters"][0]["FighterId"]] = {
        "Name": split(fight["Fighters"][0]["Name"]["FirstName"])
        + " "
        + fight["Fighters"][0]["Name"]["LastName"],
        "Odds": 100,
    }
    data[fight["Fighters"][1]["FighterId"]] = {
        "Name": split(fight["Fighters"][1]["Name"]["FirstName"])
        + " "
        + fight["Fighters"][1]["Name"]["LastName"],
        "Odds": 100,
    }
    data[data[fight["Fighters"][0]["FighterId"]]["Name"]] = 100
    data[data[fight["Fighters"][1]["FighterId"]]["Name"]] = 100
    return data


def split(name):
    names = ["" for znak in name if ord(znak) < 97]
    idx = -1
    for i in name:
        if ord(i) < 97:
            idx += 1
        names[idx] += i
    new_name = ""
    for tekst in names:
        new_name += tekst
        new_name += " "
    newName = ""
    for znak in new_name[:-1]:
        newName += znak
    return newName


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


def resolve(fight_id, fighter_id):
    url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/fight/live/{fight_id}.json"
    response = json.loads(requests.get(url).text)
    fighters = response["LiveFightDetail"]["Fighters"]
    for fighter in fighters:
        if fighter["FighterId"] == fighter_id:
            result = fighter["Outcome"]["OutcomeId"]
            if result == 2:
                return -1
            elif result == 1:
                return 1
            else:
                return 0
    return 0
