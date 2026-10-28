from flask import Flask, jsonify, render_template, request
from analytics import (
    get_overview,
    get_championship_stats,
    get_race_stats,
    get_driver_leaderboard,
    get_reliability_stats,
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/overview")
def api_overview():
    try:
        return jsonify(get_overview())
    except Exception:
        app.logger.exception("Failed to load dataset overview")
        return jsonify({"error": "Unable to load dataset overview"}), 500


@app.route("/api/championship")
def api_championship():
    try:
        return jsonify(get_championship_stats())
    except Exception:
        app.logger.exception("Failed to load championship statistics")
        return jsonify({"error": "Unable to load championship statistics"}), 500


@app.route("/api/races")
def api_races():
    try:
        return jsonify(get_race_stats())
    except Exception:
        app.logger.exception("Failed to load race statistics")
        return jsonify({"error": "Unable to load race statistics"}), 500


@app.route("/api/drivers")
def api_drivers():
    try:
        season = request.args.get("season", type=int)
        return jsonify(get_driver_leaderboard(season))
    except Exception:
        app.logger.exception("Failed to load driver leaderboard")
        return jsonify({"error": "Unable to load driver leaderboard"}), 500


@app.route("/api/reliability")
def api_reliability():
    try:
        return jsonify(get_reliability_stats())
    except Exception:
        app.logger.exception("Failed to load reliability statistics")
        return jsonify({"error": "Unable to load reliability statistics"}), 500


if __name__ == "__main__":
    app.run(debug=True)
