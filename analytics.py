import pandas as pd
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "F1 Racing Project Dataset.xlsx"
)


def _read_sheet(sheet_name):
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_FILE}. "
            "Place 'F1 Racing Project Dataset.xlsx' in the data folder."
        )
    return pd.read_excel(DATA_FILE, sheet_name=sheet_name)


def _latest_season(df):
    if df.empty or "season" not in df.columns:
        raise ValueError("The sheet has no season data.")
    return int(pd.to_numeric(df["season"], errors="coerce").max())


def get_overview():
    workbook = pd.ExcelFile(DATA_FILE)
    result = {}
    for sheet in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet)
        result[sheet] = {
            "rows": int(len(df)),
            "columns": [str(column) for column in df.columns],
        }
    return result


def get_championship_stats():
    df = _read_sheet("championship_standings")
    season = _latest_season(df)
    season_df = df[pd.to_numeric(df["season"], errors="coerce") == season].copy()

    if season_df.empty:
        raise ValueError("No championship rows found for the latest season.")

    for col in ["points", "wins", "podiums", "pole_positions", "dnfs"]:
        if col in season_df.columns:
            season_df[col] = pd.to_numeric(season_df[col], errors="coerce").fillna(0)

    sort_cols = [c for c in ["points", "wins", "podiums"] if c in season_df.columns]
    season_df = season_df.sort_values(sort_cols, ascending=[False] * len(sort_cols))

    leader = season_df.iloc[0]
    leaderboard = []
    for _, row in season_df.head(10).iterrows():
        leaderboard.append({
            "position": int(row["driver_position"]) if pd.notna(row.get("driver_position")) else len(leaderboard) + 1,
            "driver": str(row.get("driver", "Unknown")),
            "team": str(row.get("team", "Unknown")),
            "points": int(row.get("points", 0)),
            "wins": int(row.get("wins", 0)),
            "podiums": int(row.get("podiums", 0)),
            "poles": int(row.get("pole_positions", 0)),
            "dnfs": int(row.get("dnfs", 0)),
        })

    return {
        "season": season,
        "driver_count": int(season_df["driver"].nunique()),
        "leader": str(leader["driver"]),
        "leader_team": str(leader.get("team", "Unknown")),
        "leader_points": int(leader.get("points", 0)),
        "leader_wins": int(leader.get("wins", 0)),
        "leader_podiums": int(leader.get("podiums", 0)),
        "leader_poles": int(leader.get("pole_positions", 0)),
        "leader_dnfs": int(leader.get("dnfs", 0)),
        "leaderboard": leaderboard,
    }


def get_race_stats():
    df = _read_sheet("race_results")
    season = _latest_season(df)
    season_df = df[pd.to_numeric(df["season"], errors="coerce") == season].copy()

    race_count = int(df["race_id"].nunique())
    season_race_count = int(season_df["race_id"].nunique())

    # is_wet_race and race_id are repeated per driver; count each race only once.
    race_weather = season_df.groupby("race_id", dropna=True)["is_wet_race"].max()
    wet_races = int((pd.to_numeric(race_weather, errors="coerce").fillna(0) == 1).sum())

    return {
        "latest_season": season,
        "total_races": race_count,
        "season_races": season_race_count,
        "drivers_in_latest_season": int(season_df["driver"].nunique()),
        "wet_races_in_latest_season": wet_races,
        "dnfs_in_latest_season": int(pd.to_numeric(season_df["dnf"], errors="coerce").fillna(0).sum()),
        "fastest_laps_in_latest_season": int(pd.to_numeric(season_df["fastest_lap"], errors="coerce").fillna(0).sum()),
        "total_drs_overtakes_in_latest_season": int(pd.to_numeric(season_df["drs_overtakes"], errors="coerce").fillna(0).sum()),
        "dataset_rows": int(len(df)),
    }


def get_driver_leaderboard(season=None):
    df = _read_sheet("championship_standings")
    available_season = _latest_season(df)
    selected_season = int(season) if season is not None else available_season
    df["season"] = pd.to_numeric(df["season"], errors="coerce")
    season_df = df[df["season"] == selected_season].copy()

    if season_df.empty:
        return {
            "season": selected_season,
            "available_seasons": sorted(int(s) for s in df["season"].dropna().unique()),
            "drivers": [],
        }

    for col in ["points", "wins", "podiums", "pole_positions", "dnfs"]:
        if col in season_df.columns:
            season_df[col] = pd.to_numeric(season_df[col], errors="coerce").fillna(0)

    season_df = season_df.sort_values(
        [c for c in ["points", "wins", "podiums"] if c in season_df.columns],
        ascending=False,
    )

    drivers = []
    for idx, (_, row) in enumerate(season_df.iterrows(), start=1):
        drivers.append({
            "position": int(row["driver_position"]) if pd.notna(row.get("driver_position")) else idx,
            "driver": str(row.get("driver", "Unknown")),
            "team": str(row.get("team", "Unknown")),
            "points": int(row.get("points", 0)),
            "wins": int(row.get("wins", 0)),
            "podiums": int(row.get("podiums", 0)),
            "poles": int(row.get("pole_positions", 0)),
            "dnfs": int(row.get("dnfs", 0)),
        })

    return {
        "season": selected_season,
        "available_seasons": sorted(int(s) for s in df["season"].dropna().unique()),
        "drivers": drivers,
    }


def get_reliability_stats():
    df = _read_sheet("race_results")
    season = _latest_season(df)
    season_df = df[pd.to_numeric(df["season"], errors="coerce") == season].copy()

    dnf_flag = pd.to_numeric(season_df["dnf"], errors="coerce").fillna(0)
    dnf_rows = season_df[dnf_flag == 1].copy()

    if "dnf_reason" in dnf_rows.columns:
        reasons = (
            dnf_rows["dnf_reason"]
            .fillna("Unspecified")
            .astype(str)
            .replace({"": "Unspecified", "nan": "Unspecified"})
            .value_counts()
            .head(8)
        )
        reason_list = [{"reason": str(reason), "count": int(count)} for reason, count in reasons.items()]
    else:
        reason_list = []

    team_col = "team" if "team" in dnf_rows.columns else None
    team_dnfs = []
    if team_col:
        counts = dnf_rows[team_col].fillna("Unknown").value_counts().head(8)
        team_dnfs = [{"team": str(team), "dnfs": int(count)} for team, count in counts.items()]

    total_entries = len(season_df)
    total_dnfs = int(dnf_flag.sum())

    return {
        "season": season,
        "total_entries": int(total_entries),
        "total_dnfs": total_dnfs,
        "dnf_rate_pct": round((total_dnfs / total_entries) * 100, 1) if total_entries else 0,
        "dnf_reasons": reason_list,
        "teams_by_dnfs": team_dnfs,
    }
