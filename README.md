# F1 Race Intelligence

A Formula 1 data analytics web app built with Flask, pandas, Excel and Tableau Public.

## Features

- Tableau Public dashboard embedded in a custom dark-themed website
- Flask JSON API for workbook overview, championship standings, race statistics, driver leaderboard and reliability summaries
- Live frontend cards populated from API responses
- Driver championship comparison table
- DNF reasons and teams-by-DNF summaries
- Responsive layout and mobile-friendly tables

## Project structure

```text
f1-race-intelligence/
├── app.py
├── analytics.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── F1 Racing Project Dataset.xlsx
├── templates/
│   └── index.html
└── static/
```

## Run locally

1. Put `F1 Racing Project Dataset.xlsx` inside the `data/` folder.
2. Create and activate a virtual environment.

   **Windows PowerShell**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Start the app:
   ```powershell
   python app.py
   ```

5. Open `http://127.0.0.1:5000/`.

## API endpoints

- `GET /api/overview` — sheet names, row counts and columns
- `GET /api/championship` — latest-season championship leader and top 10
- `GET /api/races` — race and season summary
- `GET /api/drivers` — driver standings for the latest season
- `GET /api/drivers?season=2025` — standings for a chosen season, if present
- `GET /api/reliability` — latest-season DNF rate, retirement reasons and teams by DNFs

## Data and interpretation notes

- The app reads the workbook from `data/F1 Racing Project Dataset.xlsx`.
- Season summaries use the maximum `season` value in the workbook; the latest season may be incomplete.
- “Total races” counts unique `race_id` values, not driver-race rows.
- DNF totals and rates are calculated from the workbook's `dnf` flag. Confirm the source's encoding before treating these values as official statistics.
- Tableau Public must be reachable from the browser for its embedded dashboard to load.
- Do not commit the Excel workbook to a public repository unless you have permission to redistribute it. If deploying, make sure the deployment environment has access to the workbook and update `.gitignore` only if you intentionally want to include it.

## Deployment notes

For a host that supports Python web apps, install from `requirements.txt` and use a production server such as:

```bash
gunicorn app:app
```

Configure the hosting service's start command as `gunicorn app:app`. Ensure the workbook is present at the expected path in the deployed environment. The local Flask development server (`python app.py`) is for local development, not production.
