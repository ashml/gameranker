# Game Ranker

Desktop Python application for ranking video games using pairwise comparisons and TrueSkill.

## Features
- Import games from `.docx` or `.txt` (one game per line).
- Pairwise comparisons: left better, draw, right better.
- TrueSkill-based ratings mapped to 0–100.
- SQLite storage (persistent volume in Docker).
- Export ratings to `.txt` or `.docx`.
- Optional RAWG API integration for cover images.

## Requirements
- Docker (recommended)
- Or Python 3.11+ with `pip`

## Quick start (Docker)

```bash
xhost +local:root
RAWG_API_KEY=your_key_here docker compose up --build
```

> For Linux desktop usage, X11 forwarding is required. If you do not have a RAWG API key, the app will use a placeholder image.

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Data
- Database stored at `data/database.sqlite`.
- Provide your own `.docx` or `.txt` file with one game per line for imports.

Input format supports optional initial score per line:

```
Game Name [98]
Game Name 2
Game Name 3 [87]
```

If score is missing, game starts from 50 with maximum uncertainty.

## Usage
1. Use **Файл → 📂 Импорт .docx** or **📂 Импорт .txt** to load games.
2. Compare games with buttons or hotkeys:
   - Left arrow: left better
   - Up arrow: draw
   - Right arrow: right better
3. Export results with **Файл → 📤 Экспорт .txt** or **.docx**.

## RAWG API
Set `RAWG_API_KEY` to download cover images. Without it, a placeholder image is used.

## Project structure
```
app/
  main.py
  gui/
  core/
  db/
  services/
config.py
```
