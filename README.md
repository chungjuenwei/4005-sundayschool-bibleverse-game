# Bible Verse Memory Game

A simple terminal game that shows a Bible verse reference and a verse with one missing word. The player looks up the verse in their Bible and types the missing word.

## Files

- `play_verse_game.py` - game script
- `verses.csv` - verse data in CSV format

## CSV format

Each row in `verses.csv` uses four columns:

- `reference` - chapter and verse location
- `verse` - verse text with a blank `___`
- `answer` - the missing word to validate
- `difficulty` - one of `easy`, `medium`, `hard`

The game asks you to pick a difficulty level before starting.

## SQLite conversion

The `SUPER DUPER DIFFICULT` mode uses `bible_NKJV.db` for random NKJV verse selection. If the database is missing, run:

```powershell
python .\convert_bible_nkjv_to_sqlite.py
```

This creates `bible_NKJV.db` from `bible_NKJV.csv` and adds a version/language index for faster lookups.

## Run the game

Open PowerShell, change folder to the repo, then run:

```powershell
python .\play_verse_game.py
```

Type the missing word and press Enter. If the answer is wrong, the game prompts you to try again.

## References
The csv file was found from this repo. 

It also contains other versions other than NKJV, which could be useful for other projects.

https://github.com/alshival/super_bible/tree/main/SUPER_BIBLE/version_files