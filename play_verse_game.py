import csv
import os
import pathlib
import random
import re
import sqlite3
import sys

DATA_FILE = pathlib.Path(__file__).with_name("verses.csv")
SUPER_BIBLE_CSV_FILE = pathlib.Path(__file__).with_name("bible_NKJV.csv")
SUPER_BIBLE_DB_FILE = pathlib.Path(__file__).with_name("bible_NKJV.db")
FILLER_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "with", "for", "is", "was",
    "were", "be", "been", "being", "as", "at", "by", "from", "this", "that", "these", "those",
    "his", "her", "their", "its", "h e", "she", "it", "they", "them", "we", "you", "i", "me",
    "my", "mine", "your", "yours", "our", "ours", "who", "whom", "whose", "which", "what", "when",
    "where", "why", "how", "not", "no", "yes", "so", "if", "than", "then", "too", "very",
    "can", "could", "shall", "should", "will", "would", "may", "might", "must", "do", "does", "did",
    "done", "am", "are", "dont", "doesnt", "cannot", "cant", "youre", "im", "it's", "its"
}


def clear_screen() -> None:
    command = "cls" if os.name == "nt" else "clear"
    os.system(command)


def normalize(text: str) -> str:
    return "".join(ch for ch in text.lower().strip() if ch.isalnum() or ch.isspace())


def load_verses(path: pathlib.Path):
    if not path.exists():
        print(f"Error: data file not found: {path}")
        sys.exit(1)

    verses = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for line_no, row in enumerate(reader, start=2):
            reference = row.get("reference", "").strip()
            verse = row.get("verse", "").strip()
            answer = row.get("answer", "").strip()
            difficulty = row.get("difficulty", "easy").strip().lower()

            if not reference or not verse or not answer or difficulty not in {"easy", "medium", "hard"}:
                print(f"Skipping invalid row {line_no}: incomplete or invalid data")
                continue

            verses.append((reference, verse, answer, difficulty))
    return verses


def create_super_db(csv_path: pathlib.Path, db_path: pathlib.Path) -> None:
    if not csv_path.exists():
        print(f"Error: source CSV not found: {csv_path}")
        sys.exit(1)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY,
            testament TEXT,
            book TEXT,
            title TEXT,
            chapter INTEGER,
            verse INTEGER,
            text TEXT,
            version TEXT,
            language TEXT
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_verses_version_language ON verses(version, language)"
    )

    rows = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for line_no, row in enumerate(reader, start=2):
            testament = row.get("testament", "").strip()
            book = row.get("book", "").strip()
            title = row.get("title", "").strip()
            chapter = row.get("chapter", "").strip()
            verse_no = row.get("verse", "").strip()
            text = row.get("text", "").strip()
            version = row.get("version", "").strip()
            language = row.get("language", "").strip()

            if not title or not chapter or not verse_no or not text or not version or not language:
                continue

            try:
                chapter_int = int(chapter)
                verse_int = int(verse_no)
            except ValueError:
                continue

            rows.append((
                testament,
                book,
                title,
                chapter_int,
                verse_int,
                text,
                version,
                language,
            ))

    cursor.executemany(
        "INSERT INTO verses (testament, book, title, chapter, verse, text, version, language) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def ensure_super_db() -> None:
    if SUPER_BIBLE_DB_FILE.exists():
        return
    create_super_db(SUPER_BIBLE_CSV_FILE, SUPER_BIBLE_DB_FILE)


def normalize_word(word: str) -> str:
    return re.sub(r"[^a-zA-Z']+", "", word).lower()


def choose_blank_word(text: str) -> str:
    words = [normalize_word(word) for word in re.findall(r"\b[\w']+\b", text)]
    candidates = [word for word in words if word and word not in FILLER_WORDS and not word.isnumeric() and len(word) > 3]
    if not candidates:
        candidates = [word for word in words if word and not word.isnumeric() and len(word) > 1]
    return random.choice(candidates)


def format_verse_with_blank(text: str, blank_word: str) -> str:
    placeholder = "[" + "_" * len(blank_word) + "]"
    blank_pattern = re.compile(rf"\b{re.escape(blank_word)}\b", re.IGNORECASE)
    return blank_pattern.sub(placeholder, text, count=1)


def load_super_verse(path: pathlib.Path):
    ensure_super_db()

    with sqlite3.connect(str(path)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(id), MAX(id) FROM verses WHERE version = ? AND language = ?",
            ("NKJV", "EN"),
        )
        row = cursor.fetchone()
        if not row or row[0] is None or row[1] is None:
            print(f"No NKJV verses found in SQLite database: {path}")
            sys.exit(1)

        min_id, max_id = row
        for _ in range(10):
            random_id = random.randint(min_id, max_id)
            cursor.execute(
                "SELECT title, chapter, verse, text FROM verses WHERE id >= ? AND version = ? AND language = ? ORDER BY id LIMIT 1",
                (random_id, "NKJV", "EN"),
            )
            result = cursor.fetchone()
            if result:
                title, chapter, verse_no, text = result
                break
        else:
            cursor.execute(
                "SELECT title, chapter, verse, text FROM verses WHERE version = ? AND language = ? ORDER BY RANDOM() LIMIT 1",
                ("NKJV", "EN"),
            )
            result = cursor.fetchone()
            if not result:
                print(f"No NKJV verses found in SQLite database: {path}")
                sys.exit(1)
            title, chapter, verse_no, text = result

    reference = f"{title} {chapter}:{verse_no}"
    answer = choose_blank_word(text)
    display_verse = format_verse_with_blank(text, answer)
    return reference, display_verse, answer, "super duper difficult"


def select_difficulty() -> str:
    while True:
        clear_screen()
        print("Bible Verse Lookup Challenge")
        print("Choose a difficulty level to begin your practice.")
        print("1) easy               - quick start and familiar verses")
        print("2) medium             - helpful lookup practice")
        print("3) SUPER DUPER DIFFICULT - extreme random NKJV challenge")
        # print("4) all                - mixed practice")

        choice = input("Choose 1-3 or type easy/medium/hard: ").strip().lower()
        if choice in {"1", "easy"}:
            return "easy"
        if choice in {"2", "medium"}:
            return "medium"
        if choice in {"3", "hard", "super", "super duper", "super duper difficult"}:
            return "hard"
        # if choice in {"4", "all"}:
        #     return "all"

        print("Invalid choice. Press Enter to try again.")
        input()


def ask_question(reference: str, verse: str, answer: str, difficulty: str) -> None:
    expected = normalize(answer)
    message = ""

    while True:
        clear_screen()
        print("Bible Verse Lookup Challenge")
        print("Read the reference, look up the verse in your Bible, and fill the blank word.")

        if message:
            print(f"\n{message}")

        print(f"\n{reference}    [difficulty: {difficulty}]")
        print(verse)
        print("")
        guess = input("Enter the missing word (or type 'quit' to exit): ").strip()

        if not guess:
            message = "Please type the missing word."
            continue

        if guess.lower() == "quit":
            print("Goodbye. Come back soon.")
            sys.exit(0)

        if normalize(guess) == expected:
            print("\n✅ Correct!\n")
            input("Press Enter to continue...")
            return

        message = "❌ Try again. Check the verse and fill the blank."


def main():
    verses = load_verses(DATA_FILE)
    if not verses:
        print("No verses found. Add rows to verses.csv and try again.")
        return

    difficulty = select_difficulty()
    if difficulty == "hard":
        reference, verse, answer, verse_difficulty = load_super_verse(SUPER_BIBLE_DB_FILE)
        print("Bible Verse Lookup Challenge")
        print("Read the reference, look up the verse in your Bible, and fill the blank word.")
        print("Difficulty selected: SUPER DUPER DIFFICULT\n")
        ask_question(reference, verse, answer, verse_difficulty)
        return

    if difficulty != "all":
        verses = [item for item in verses if item[3] == difficulty]

    if not verses:
        print(f"No verses found for difficulty '{difficulty}'.")
        return

    print("Bible Verse Lookup Challenge")
    print("Read the reference, look up the verse in your Bible, and fill the blank word.")
    print(f"Difficulty selected: {difficulty}\n")

    for reference, verse, answer, verse_difficulty in verses:
        ask_question(reference, verse, answer, verse_difficulty)

    print("Well done! You completed all the verse blanks.")


if __name__ == "__main__":
    main()
