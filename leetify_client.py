import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

LEETIFY_API_KEY = os.getenv("LEETIFY_API_KEY")
BASE_URL = "https://api-public.cs-prod.leetify.com"
STEAM64_BASE = 76561197960265728
USER_AGENT = "CS2StatsTracker/1.0"


def _headers():
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if LEETIFY_API_KEY:
        headers["_leetify_key"] = LEETIFY_API_KEY
    return headers


def resolve_steam64(query: str):
    """แปลงข้อความค้นหาเป็น Steam64 ID (ตัวเลข 17 หลัก)"""
    if not query:
        return None

    q = query.strip()

    match = re.search(r"steamcommunity\.com/profiles/(\d{15,17})", q, re.I)
    if match:
        return match.group(1)

    match = re.search(r"steamcommunity\.com/id/([^/?#]+)", q, re.I)
    if match:
        return _resolve_vanity(match.group(1))

    match = re.match(r"^STEAM_[0-9]:([01]):(\d+)$", q, re.I)
    if match:
        y, z = int(match.group(1)), int(match.group(2))
        return str(STEAM64_BASE + z * 2 + y)

    match = re.match(r"^\[U:1:(\d+)\]$", q, re.I)
    if match:
        return str(STEAM64_BASE + int(match.group(1)))

    if q.isdigit() and len(q) == 17:
        return q

    if q.isdigit() and 1 <= len(q) <= 10:
        return str(STEAM64_BASE + int(q))

    if re.match(r"^[A-Za-z0-9_\-]+$", q):
        return _resolve_vanity(q)

    return None


def _resolve_vanity(vanity: str):
    try:
        response = requests.get(
            f"https://steamcommunity.com/id/{vanity}/?xml=1",
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        match = re.search(r"<steamID64>(\d{15,17})</steamID64>", response.text)
        if match:
            return match.group(1)
    except requests.exceptions.RequestException:
        return None
    return None


def _skill_value(value):
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0


def _skill_bar(value):
    score = _skill_value(value)
    if abs(score) <= 1.5:
        return max(0, min(100, round(score * 100, 2)))
    return max(0, min(100, score))


def _normalize_player(data: dict):
    winrate = data.get("winrate", 0) or 0
    try:
        winrate = float(winrate)
    except (TypeError, ValueError):
        winrate = 0
    if winrate <= 1:
        winrate *= 100

    ranks = data.get("ranks") or {}
    rating = data.get("rating") or data.get("ratings") or {}

    return {
        "name": data.get("name", "N/A"),
        "steam64_id": data.get("steam64_id"),
        "totalMatches": data.get("total_matches", data.get("totalMatches", 0)),
        "winRate": round(winrate, 2),
        "ranks": {
            "premier": ranks.get("premier"),
            "faceit": ranks.get("faceit"),
        },
        "ratings": {
            "aim": _skill_value(rating.get("aim", 0)),
            "positioning": _skill_value(rating.get("positioning", 0)),
            "utility": _skill_value(rating.get("utility", 0)),
            "clutch": _skill_value(rating.get("clutch", 0)),
        },
        "rating_bars": {
            "aim": _skill_bar(rating.get("aim", 0)),
            "positioning": _skill_bar(rating.get("positioning", 0)),
            "utility": _skill_bar(rating.get("utility", 0)),
            "clutch": _skill_bar(rating.get("clutch", 0)),
        },
        "raw": data,
    }


def _normalize_match(match: dict, steam64_id: str):
    scores = match.get("team_scores") or match.get("score") or match.get("teamScores") or []
    if scores and isinstance(scores[0], dict):
        team_scores = [item.get("score", 0) for item in scores]
    else:
        team_scores = list(scores)[:2]

    won = None
    stats = match.get("stats") or []
    player_stats = next(
        (item for item in stats if str(item.get("steam64_id")) == str(steam64_id)),
        None,
    )
    if player_stats:
        won = (player_stats.get("rounds_won") or 0) > (player_stats.get("rounds_lost") or 0)
    elif match.get("outcome"):
        won = str(match.get("outcome")).lower() == "win"
    else:
        won = bool(match.get("won"))

    date_value = (
        match.get("finished_at")
        or match.get("startedAt")
        or match.get("started_at")
        or ""
    )

    return {
        "mapName": match.get("map_name") or match.get("mapName") or "Unknown",
        "won": won,
        "teamScores": team_scores,
        "startedAt": str(date_value),
    }


def get_player_data(query: str):
    steam64_id = resolve_steam64(query)
    if not steam64_id:
        return None

    try:
        response = requests.get(
            f"{BASE_URL}/v3/profile",
            params={"steam64_id": steam64_id},
            headers=_headers(),
            timeout=20,
        )
        if response.status_code != 200:
            return None
        data = response.json()
        if not isinstance(data, dict) or not data.get("name"):
            return None
        player = _normalize_player(data)
        player["steam64_id"] = steam64_id
        return player
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None


def get_match_history(query: str, limit: int = 5):
    steam64_id = resolve_steam64(query)
    if not steam64_id:
        return []

    try:
        response = requests.get(
            f"{BASE_URL}/v3/profile/matches",
            params={"steam64_id": steam64_id},
            headers=_headers(),
            timeout=30,
        )
        if response.status_code != 200:
            return []
        data = response.json()
        if isinstance(data, dict):
            matches = data.get("matches", [])
        else:
            matches = data or []
        return [_normalize_match(match, steam64_id) for match in matches[:limit]]
    except requests.exceptions.RequestException:
        return []
    except Exception:
        return []
