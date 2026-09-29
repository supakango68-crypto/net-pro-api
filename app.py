from flask import Flask, jsonify, render_template, request

from leetify_client import get_match_history, get_player_data

app = Flask(__name__)


def compare_players(id1: str, id2: str):
    """เปรียบเทียบผู้เล่น 2 คน แล้วคืนค่าเป็น dict"""
    player1 = get_player_data(id1)
    player2 = get_player_data(id2)

    if not player1 or not player2:
        return None

    ratings1 = player1.get("ratings") or {}
    ratings2 = player2.get("ratings") or {}

    categories = [
        ("Aim", ratings1.get("aim", 0), ratings2.get("aim", 0)),
        ("Positioning", ratings1.get("positioning", 0), ratings2.get("positioning", 0)),
        ("Utility", ratings1.get("utility", 0), ratings2.get("utility", 0)),
        ("Clutch", ratings1.get("clutch", 0), ratings2.get("clutch", 0)),
    ]

    comparison = []
    for name, score1, score2 in categories:
        if score1 and score2:
            if score1 > score2:
                winner = player1.get("name", "N/A")
                result = f"{winner} เก่งกว่า ({score1} vs {score2})"
            elif score2 > score1:
                winner = player2.get("name", "N/A")
                result = f"{winner} เก่งกว่า ({score2} vs {score1})"
            else:
                winner = None
                result = f"ทั้งคู่เท่ากัน ({score1})"
        else:
            winner = None
            result = "ไม่มีข้อมูล"

        comparison.append(
            {
                "category": name,
                "score1": score1,
                "score2": score2,
                "winner": winner,
                "result": result,
            }
        )

    return {
        "player1": player1,
        "player2": player2,
        "comparison": comparison,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    player = None
    steam_id = ""
    error = None

    if request.method == "POST":
        steam_id = request.form.get("steam64_id", "").strip()
        if not steam_id:
            error = "กรุณาป้อน Steam ID หรือลิงก์โปรไฟล์ Steam"
        else:
            player = get_player_data(steam_id)
            if not player:
                error = "ไม่พบข้อมูลผู้เล่น กรุณาตรวจ Steam ID / ลิงก์โปรไฟล์ หรือว่าผู้เล่นมีข้อมูลบน Leetify"
            else:
                steam_id = player.get("steam64_id") or steam_id

    return render_template(
        "profile.html",
        player=player,
        steam_id=steam_id,
        error=error,
    )


@app.route("/matches", methods=["GET", "POST"])
def matches():
    matches_list = []
    steam_id = ""
    player_name = ""
    limit = 5
    error = None

    if request.method == "POST":
        steam_id = request.form.get("steam64_id", "").strip()
        limit_raw = request.form.get("limit", "5").strip()
        try:
            limit = int(limit_raw) if limit_raw else 5
        except ValueError:
            limit = 5
        limit = max(1, min(limit, 30))

        if not steam_id:
            error = "กรุณาป้อน Steam ID หรือลิงก์โปรไฟล์ Steam"
        else:
            player = get_player_data(steam_id)
            if player:
                player_name = player.get("name", "")
                steam_id = player.get("steam64_id") or steam_id
            matches_list = get_match_history(steam_id, limit)
            if not matches_list:
                error = "ไม่พบประวัติแมตช์ หรือผู้เล่นยังไม่มีข้อมูลบน Leetify"

    return render_template(
        "matches.html",
        matches=matches_list,
        steam_id=steam_id,
        player_name=player_name,
        limit=limit,
        error=error,
    )


@app.route("/compare", methods=["GET", "POST"])
def compare():
    player1 = None
    player2 = None
    id1 = ""
    id2 = ""
    error = None

    if request.method == "POST":
        id1 = request.form.get("id1", "").strip()
        id2 = request.form.get("id2", "").strip()
        if not id1 or not id2:
            error = "กรุณาป้อน Steam ID หรือลิงก์โปรไฟล์ทั้งสองคน"
        else:
            result = compare_players(id1, id2)
            if not result:
                error = "ไม่สามารถดึงข้อมูลผู้เล่นได้ กรุณาตรวจสอบ Steam ID / ลิงก์โปรไฟล์"
            else:
                player1 = result["player1"]
                player2 = result["player2"]
                id1 = player1.get("steam64_id") or id1
                id2 = player2.get("steam64_id") or id2

    return render_template(
        "compare.html",
        player1=player1,
        player2=player2,
        steam_id_1=id1,
        steam_id_2=id2,
        error=error,
    )


@app.route("/api/player/<player_id>")
def api_player(player_id):
    player = get_player_data(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify(player)


if __name__ == "__main__":
    app.run(debug=True)
