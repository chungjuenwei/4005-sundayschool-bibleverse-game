import csv
import sqlite3
from pathlib import Path

CSV_FILE = Path(__file__).with_name("bible_NKJV.csv")
DB_FILE = Path(__file__).with_name("bible_NKJV.db")


def create_database(csv_path: Path, db_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"Source file not found: {csv_path}")

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

            rows.append(
                (
                    testament,
                    book,
                    title,
                    chapter_int,
                    verse_int,
                    text,
                    version,
                    language,
                )
            )

    cursor.executemany(
        "INSERT INTO verses (testament, book, title, chapter, verse, text, version, language) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database(CSV_FILE, DB_FILE)
    print(f"Created SQLite database: {DB_FILE}")
