# Bible Verse Memory Game (API + SQLite)

This version of the game uses the Bible API and an SQLite cache instead of a CSV file.

## How it works

- The game asks you to choose a difficulty level.
- It fetches verse text from `https://bible-api.com/`.
- A non-filler word is removed and shown as `___`.
- You type the missing word to continue.
- Fetched verses are cached in `api_sqlite_game/verses.db`.

## Run the game

Open PowerShell in the repository folder and run:

```powershell
python .\api_sqlite_game\game.py
```

## Notes

- No `verses.csv` file is required for this version.
- The first fetch may take a moment while the API is called.
- If you run the game again, cached verses are reused from SQLite.
