from bs4 import BeautifulSoup
import requests
import json
from typing import List, Dict, Any, Optional, Union


def get_ufc_odds(event_id: int) -> Dict[str, Any]:
    """
    Fetches UFC odds for a specific event ID from the API.
    """
    ufc_url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{event_id}.json"
    return json.loads(requests.get(ufc_url).text)


def edited_ufc_odds(event_id: int) -> Dict[str, Any]:
    """
    Fetches and processes UFC odds, combining API data with scraped odds.
    """
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


def fill_odds(fights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scrapes bestfightodds.com to fill in odds for the fights.
    """
    url = "https://www.bestfightodds.com/#"
    result = requests.get(url).text

    doc = BeautifulSoup(result, "html.parser")
    # Iterate over every second tbody, as the structure of the site alternates
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


def get_bet(spans: Any) -> int:
    """
    Extracts the best bet value from a list of spans.
    """
    skip = ["▲", "▼", ""]
    bets = [int(span.text) for span in spans[1:] if span.text not in skip]
    if len(bets) == 0:
        bet = 100
    else:
        bet = max(bets)
    return bet


def trim(fight: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts relevant fight data from the raw API response.
    """
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


def split(name: str) -> str:
    """
    Splits a name string based on capitalization (e.g. "JohnDoe" -> "John Doe").
    """
    names = ["" for char in name if ord(char) < 97]
    idx = -1
    for i in name:
        if ord(i) < 97:
            idx += 1
        names[idx] += i
    new_name = ""
    for text in names:
        new_name += text
        new_name += " "
    final_name = ""
    for char in new_name[:-1]:
        final_name += char
    return final_name


def get_best_fight_odds() -> List[Dict[str, Any]]:
    """
    Scrapes the best fight odds from bestfightodds.com.
    """
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


def resolve(fight_id: int, fighter_id: int) -> int:
    """
    Resolves the outcome of a fight for a specific fighter.
    Returns 1 if won, -1 if lost, 0 if draw/unknown.
    """
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
