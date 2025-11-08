import requests
import json
import numpy as np


def get_ufc_fight(fight_id):
    ufc_url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/fight/live/{fight_id}.json"
    return json.loads(requests.get(ufc_url).text)


def get_edited_fight(fight_id):
    data = get_ufc_fight(fight_id)
    if data["LiveFightDetail"]["Fighters"][0]["Outcome"]["OutcomeId"] == 1:
        win_id = 0
        lose_id = 1
    else:
        win_id = 1
        lose_id = 0
    win = trim_fighter(data["LiveFightDetail"]["Fighters"][win_id])
    lose = trim_fighter(data["LiveFightDetail"]["Fighters"][lose_id])

    fight1 = [w - l for w, l in zip(win, lose)]
    fight1.append(1)
    fight2 = [l - w for w, l in zip(win, lose)]
    fight2.append(0)
    return fight1, fight2


def trim_fighter(fighter):
    return [
        fighter["Age"],
        fighter["Weight"],
        fighter["Height"],
        fighter["Reach"],
        fighter["Record"]["Wins"],
        fighter["Record"]["Losses"],
        fighter["Record"]["Draws"],
    ]
