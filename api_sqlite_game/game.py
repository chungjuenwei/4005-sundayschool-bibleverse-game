import json
import os
import random
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).with_name("verses.db")
API_BASE_URL = "https://bible-api.com/"

VERSE_BANK = {
    "easy": ["John 3:16", "Psalm 23:1", "Matthew 5:9"],
    "medium": ["Romans 8:28", "Philippians 4:13", "Proverbs 3:5"],
    "hard": ["Isaiah 40:31", "Hebrews 11:1", "James 1:2"],
}
ALL_REFERENCES = [reference for group in VERSE_BANK.values() for reference in group]

FILLER_WORDS = {
    "and", "the", "for", "of", "to", "in", "a", "an", "is", "it", "that", "with", "on", "at", "by",
    "as", "be", "or", "if", "so", "not", "but", "from", "your", "his", "her", "our", "their",
    "this", "which", "who", "whoever", "when", "where", "why", "how", "will", "may", "then", "also",
}


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def normalize(text: str) -> str:
    return "".join(ch for ch in text.lower().strip() if ch.isalnum())


def open_database() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS verse_cache (
            reference TEXT PRIMARY KEY,
            translation_id TEXT NOT NULL,
            text TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def get_cached_verse(conn: sqlite3.Connection, reference: str):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT translation_id, text FROM verse_cache WHERE reference = ?",
        (reference,),
    )
    row = cursor.fetchone()
    if row:
        return {
            "reference": reference,
            "translation_id": row[0],
            "text": row[1],
        }
    return None


def save_cached_verse(conn: sqlite3.Connection, reference: str, translation_id: str, text: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "REPLACE INTO verse_cache (reference, translation_id, text, fetched_at) VALUES (?, ?, ?, ?)",
        (reference, translation_id, text, datetime.utcnow().isoformat()),
    )
    conn.commit()


def fetch_verse_text(conn: sqlite3.Connection, reference: str) -> str:
    cached = get_cached_verse(conn, reference)
    if cached:
        return cached["text"]

    query = urllib.parse.quote(reference, safe="")
    url = f"{API_BASE_URL}{query}?translation=web"
    request = urllib.request.Request(url, headers={"User-Agent": "BibleVerseGame/1.0"})

    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        print(f"Error fetching verse {reference}: HTTP {error.code}")
        sys.exit(1)
    except urllib.error.URLError as error:
        print(f"Error fetching verse {reference}: {error.reason}")
        sys.exit(1)

    data = json.loads(body)
    text = data.get("text", "").strip()
    if not text:
        print(f"Error: no verse text returned for '{reference}'.")
        sys.exit(1)

    translation_id = data.get("translation_id", "web")
    save_cached_verse(conn, reference, translation_id, text)

    return text


def select_blank(text: str) -> tuple[str, str]:
    tokens = re.findall(r"\w+|[^\w]+", text)
    candidates = [
        (idx, token)
        for idx, token in enumerate(tokens)
        if token.isalpha() and token.lower() not in FILLER_WORDS and len(token) > 2
    ]

    if not candidates:
        candidates = [
            (idx, token)
            for idx, token in enumerate(tokens)
            if token.isalpha() and len(token) > 1
        ]

    if not candidates:
        return text, ""

    index, word = random.choice(candidates)
    tokens[index] = "___"
    return "".join(tokens), word


def select_difficulty() -> str:
    while True:
        clear_screen()
        print("Bible Verse Memory Game (API + SQLite)")
        print("Choose a difficulty level to begin your practice.")
        print("1) easy   - simple verses")
        print("2) medium - moderate challenge")
        print("3) hard   - stronger memory work")
        print("4) all    - mixed practice")

        choice = input("Choose 1-4 or type easy/medium/hard/all: ").strip().lower()
        if choice in {"1", "easy"}:
            return "easy"
        if choice in {"2", "medium"}:
            return "medium"
        if choice in {"3", "hard"}:
            return "hard"
        if choice in {"4", "all"}:
            return "all"

        print("Invalid choice. Press Enter to try again.")
        input()


def ask_question(reference: str, verse: str, answer: str) -> None:
    expected = normalize(answer)
    message = ""

    while True:
        clear_screen()
        print("Bible Verse Memory Game (API + SQLite)")
        print("Read the reference, look up the verse in your Bible, and fill the blank word.")

        if message:
            print(f"\n{message}")

        print(f"\n{reference}")
        print(verse)
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


def main() -> None:
    conn = open_database()
    difficulty = select_difficulty()

    if difficulty == "all":
        references = list(ALL_REFERENCES)
    else:
        references = list(VERSE_BANK[difficulty])

    random.shuffle(references)

    for reference in references:
        verse_text = fetch_verse_text(conn, reference)
        blanked_text, missing_word = select_blank(verse_text)
        if not missing_word:
            print(f"Could not prepare a blank for {reference}. Skipping.")
            continue
        ask_question(reference, blanked_text, missing_word)

    clear_screen()
    print("Bible Verse Memory Game (API + SQLite)")
    print("Well done! You completed all the verse blanks.")


if __name__ == "__main__":
    main()
