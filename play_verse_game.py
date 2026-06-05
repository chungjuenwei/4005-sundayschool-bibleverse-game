import csv
import os
import pathlib
import random
import re
import sys

DATA_FILE = pathlib.Path(__file__).with_name("verses.csv")
BIBLE_FILE = pathlib.Path(__file__).with_name("bible_NKJV.csv")
FILLER_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "with", "for", "is", "was",
    "were", "be", "been", "being", "as", "at", "by", "from", "this", "that", "these", "those",
    "his", "her", "their", "its", "he", "she", "it", "they", "them", "we", "you", "i", "me",
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


def normalize_word(word: str) -> str:
    return re.sub(r"[^a-zA-Z']+", "", word).lower()


def choose_blank_word(text: str) -> str:
    candidates = [normalize_word(word) for word in re.findall(r"\b[\w']+\b", text)]
    candidates = [word for word in candidates if word and word not in FILLER_WORDS and not word.isnumeric()]
    if not candidates:
        candidates = [normalize_word(word) for word in re.findall(r"\b[\w']+\b", text) if normalize_word(word)]
    return random.choice(candidates)


def format_verse_with_blank(text: str, blank_word: str) -> str:
    placeholder = "[___]"
    blank_pattern = re.compile(rf"\b{re.escape(blank_word)}\b", re.IGNORECASE)
    return blank_pattern.sub(placeholder, text, count=1)


def load_verse(path: pathlib.Path):
    if not path.exists():
        print(f"Error: data file not found: {path}")
        sys.exit(1)

    verses = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for line_no, row in enumerate(reader, start=2):
            book = row.get("title", "").strip()
            chapter = row.get("chapter", "").strip()
            verse_no = row.get("verse", "").strip()
            text = row.get("text", "").strip()

            if not book or not chapter or not verse_no or not text:
                continue

            reference = f"{book} {chapter}:{verse_no}"
            answer = choose_blank_word(text)
            display_verse = format_verse_with_blank(text, answer)
            verses.append((reference, display_verse, answer, "super duper difficult"))

    if not verses:
        print(f"No verses found in {path}.")
        sys.exit(1)

    return random.choice(verses)


def select_difficulty() -> str:
    while True:
        clear_screen()
        print("Bible Verse Memory Game")
        print("Choose a difficulty level to begin your practice.")
        print("1) easy               - quick start and familiar verses")
        print("2) medium             - helpful lookup practice")
        print("3) SUPER DUPER DIFFICULT - extreme random NKJV challenge")
        print("4) all                - mixed practice")

        choice = input("Choose 1-4 or type easy/medium/hard/all: ").strip().lower()
        if choice in {"1", "easy"}:
            return "easy"
        if choice in {"2", "medium"}:
            return "medium"
        if choice in {"3", "hard", "super", "super duper", "super duper difficult"}:
            return "hard"
        if choice in {"4", "all"}:
            return "all"

        print("Invalid choice. Press Enter to try again.")
        input()


def ask_question(reference: str, verse: str, answer: str, difficulty: str) -> None:
    expected = normalize(answer)
    message = ""

    while True:
        clear_screen()
        print("Bible Verse Memory Game")
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
        reference, verse, answer, verse_difficulty = load_verse(BIBLE_FILE)
        print("Bible Verse Memory Game")
        print("Read the reference, look up the verse in your Bible, and fill the blank word.")
        print("Difficulty selected: SUPER DUPER DIFFICULT\n")
        ask_question(reference, verse, answer, verse_difficulty)
        return

    if difficulty != "all":
        verses = [item for item in verses if item[3] == difficulty]

    if not verses:
        print(f"No verses found for difficulty '{difficulty}'.")
        return

    print("Bible Verse Memory Game")
    print("Read the reference, look up the verse in your Bible, and fill the blank word.")
    print(f"Difficulty selected: {difficulty}\n")

    for reference, verse, answer, verse_difficulty in verses:
        ask_question(reference, verse, answer, verse_difficulty)

    print("Well done! You completed all the verse blanks.")


if __name__ == "__main__":
    main()
