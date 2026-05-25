# Bible Verse Memory Game

A simple terminal game that shows a Bible verse reference and a verse with one missing word. The player looks up the verse in their Bible and types the missing word.

## Files

- `play_verse_game.py` - game script
- `verses.csv` - verse data in CSV format
- `api_sqlite_game/` - API-based game using SQLite cache instead of CSV

## CSV format

Each row in `verses.csv` uses four columns:

- `reference` - chapter and verse location
- `verse` - verse text with a blank `___`
- `answer` - the missing word to validate
- `difficulty` - one of `easy`, `medium`, `hard`

The game asks you to pick a difficulty level before starting.

## Run the game

Open PowerShell, change folder to the repo, then run:

```powershell
python .\play_verse_game.py
```

Type the missing word and press Enter. If the answer is wrong, the game prompts you to try again.
