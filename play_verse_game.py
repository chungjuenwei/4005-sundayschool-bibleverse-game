import csv
import os
import pathlib
import sys

DATA_FILE = pathlib.Path(__file__).with_name("verses.csv")


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


def select_difficulty() -> str:
    while True:
        clear_screen()
        print("Bible Verse Memory Game")
        print("Choose a difficulty level to begin your practice.")
        print("1) easy   - quick start and familiar verses")
        print("2) medium - helpful lookup practice")
        print("3) hard   - stronger memory challenge")
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
