# Kotoba Lens

> **Turn any image of Japanese text into an ordered, level-tagged vocabulary list.**

Kotoba Lens is a desktop application that extracts Japanese vocabulary from manga images and outputs a **difficulty-ranked** list of the words
featured in the image. It combines **PaddleOCR** for text detection, a **JMDict** backing
dictionary, a **de-inflector** to resolve conjugated verbs/adjectives back to their dictionary
form, and a **custom difficulty-scoring** system so you immediately see which words are worth
studying next.

---

## ✨ Features

- **Japanese OCR** powered by PaddleOCR (PP-OCRv6 medium detection model), running locally with no
  cloud dependency.
- **Speech-bubble grouping** — detected text boxes that sit close together in the same horizontal
  band are stitched into complete, natural text lines.
- **Furigana removal** — small annotation text is filtered out so it doesn't pollute extraction.
- **Dictionary lookup** against a **JMDict**-derived SQLite database (`entries` table).
- **De-inflection engine** — inflected verbs/adjectives are reduced to their dictionary lemmas via
  a BFS over hand-written morphological rules (`deinflect_rules.json`), with condition rules for
  verb class + conjugation constraints.
- **Difficulty scoring** — every word is assigned a numeric score combining JLPT level, kanji
  difficulty, “common” frequency flag, and part-of-speech certainty. Words are returned **ordered
  by level**.
- **Persistence** — books, images, and words (plus image↔word ordering) are stored in a SQLite
  database, so results can be queried later without re-running OCR.

---

## Tech Stack

| Area              | Technology                                              | Notes                                        |
| ----------------- | ------------------------------------------------------- | -------------------------------------------- |
| **Language**      | Python 3.12                                             |                                              |
| **OCR**           | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 3.7 / PaddlePaddle 3.2 / PaddleX 3.7 | `lang="japan"`, doc orientation/unwarping & textline orientation disabled |
| **Dictionary**    | JMDict (via `jmdictExtended.json`)                      | Wik structured, stored in SQLite             |
| **Kanji data**     | KANJIS flat file (`.json`)                              | grade, frequency, stroke count               |
| **Desktop GUI**     | [PySide6](https://pypi.org/project/PySide6/) (Qt for Python) 6.11 |                                            |
| **Database**       | SQLite                                                  | `dictionary.db`, `kanji.db`, `main.db`       |
| **Data structures** | `dataclasses`, `deque` (BFS)                            |                                              |

**Model:** PP-OCRv6 medium detection model via PaddleOCR (`lang="japan"`).

---

## How it works (processing pipeline)

```
                ┌──────────────────────────────────────────────┐
  folder/image  │                  services.py                 │
   input        │                                              │
 ─────────────► │  import_folder() / image_process()           │
                └──────────────────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────────────────────┐
                │                   ocr.py                      │
                │  extract_text()   → OCRResult (text, box,     │
                │                                poly, score)   │
                │  clean_text()     → sort R→L, remove furigana,│
                │                    group boxes into lines     │
                └───────────────────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────────────────────┐
                │              parser/parser.py + deinflect.py  │
                │  parse()   → sliding window (≤10 chars) lookup│
                │            → deinflect() BFS on conjugation   │
                │  look_up() → entries table (JMDict)           │
                └───────────────────────────────────────────────┘
                                │
                                ▼
                      sort words by score (desc)
                                │
                                ▼
                ┌──────────────────────────────────────────────┐
                │               DAO.py + schema.py             │
                │  add_book() → add_image() → add_word()       │
                │  persists into main.db (BOOKS / IMAGES /     │
                │  WORDS / IMAGES_WORDS)                       │
                └──────────────────────────────────────────────┘
                                │
                                ▼
               GUI: ImageViewerApp  reads WORDS via get_words_from_image()
```

**The word-level loops are worth calling out:**

1. **OCR cleaning** (`ocr.clean_text`) — boxes are sorted right-to-left (Japanese reading order),
   boxes whose width is below `0.6 ×` the median box height are dropped as *furigana*, then
   horizontally neighbouring boxes in the same vertical band become part of the same line /
   speech bubble.
2. **Tokenization + de-inflection** (`parser.parse`) — starting at each character, substrings up to
   10 chars long are tested against the dictionary. If an inflected surface form isn't found
   directly, `deinflect.deinflect()` expands the candidate into possible dictionary form using a
   BFS over conjugation rules (with `conditions_in` / `conditions_out` for verb/vowel-class /
   politeness constraints). The first match consumes the examined span.
3. **Scoring & ordering** — extracted words are sorted by `score` descending, i.e. *rarest /
   most-challenging words first*. This ordering is stored per image in `IMAGES_WORDS.WORD_ORDER`.

---

## ⚙️ Installation

Requires Python 3.12+ and a PaddleOCR-compatible PaddlePaddle install; see the [PaddleOCR install guide](https://www.paddleocr.ai/main/en/install.html) for platform-specific wheels.

### Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install paddlepaddle paddleocr
cd src
pip install -r requirements.txt
```

PaddleOCR and PaddlePaddle are regular PyPI packages, so the same `pip install` works on Linux, macOS, and Windows. GPU support is `pip install paddlepaddle-gpu`.

Notes:

- `src/env/` is a gitignored working-install snapshot; use your own virtual environment instead.
- `src/database/json/jmdictExtended.json` (≈167 MB) is not tracked; it is only needed to rebuild `dictionary.db` from source.

---

## Usage

### GUI mode (recommended)

```bash
cd src
python main.py
```

1. Click **📁 Select Folder** and pick a folder full of images.
2. Every image in the folder is OCR'd and parsed; the book, images and words load into the DB.
3. Pick an image in the left list → the vocabulary for that page appears in the right list,
   ordered by difficulty (top words are the rarest/most challenging).

### Folder import

`services.import_folder(fld_path, model, rules, cur)` walks a directory, creates a **BOOKS**
record, and bulk-processes every `.png /.jpg /.jpeg /.bmp /.gif /.webp` file in sorted order.

---

## 🗄 Database schema

Stored as `src/database/main.db`.

### `BOOKS`
| Column      | Type      | Notes                                        |
|-------------|-----------|----------------------------------------------|
| `BOOK_ID`   | INTEGER PK| Auto-increment                              |
| `NAME`      | TEXT      | Folder name                                |
| `PATH`      | TEXT      | Folder path (unique-enforced in app)       |
| `CREATED_AT`| TEXT   | `datetime(now, 'localtime')`              |

### `IMAGES`
| Column       | Type      | Notes                                        |
|--------------|-----------|----------------------------------------------|
| `IMG_ID`     | INTEGER PK| auto-increment                              |
| `BOOK_ID`    | INTEGER FK| → `BOOKS.BOOK_ID`                          |
| `PATH`       | TEXT      | unique per file; skip if already imported   |
| `OCR_RESULT` | TEXT      | all raw text lines joined with `\n`        |
| `IMPORT_TIME`| TEXT   | `datetime(now, 'localtime')`              |
| `PAGE`       | INTEGER   | 1-based page number                        |

### `WORDS`
| Column    | Type     | Notes                                              |
|-----------|----------|---------------------------------------------------|
| `WORD_ID` | INTEGER PK | auto-increment                                  |
| `LEMMA`   | TEXT   | dictionary form (de-inflected)                 |
| `POS`     | TEXT   | part of speech (e.g. `noun\|verb`)             |
| `READING` | TEXT   | reading                                         |
| `MEANING` | TEXT   | glossary text                                  |
| `SCORE`   | REAL   | difficulty score (higher = more rare)          |

### `IMAGES_WORDS` (join)
| Column       | Type        | Notes                                        |
|--------------|-------------|----------------------------------------------|
| `IMAGE_ID`   | INTEGER FK  | → `IMAGES.IMG_ID`                          |
| `WORD_ID`    | INTEGER FK  | → `WORDS.WORD_ID`                          |
| `WORD_ORDER` | INTEGER     | display order (by score) within the image   |
| **PK**       |             | `(IMAGE_ID, WORD_ID, WORD_ORDER)`           |

### Supporting dictionaries

- **`dictionary.db`** — `entries(id, expression, reading, pos, glossary, jlpt, common, tag, misc, score)`.
  Indexed on `(expression)` and `(reading)`. `look_up()` requires `expression = ? AND pos != ''`
  and only accepts an unambiguous (single-row) match.
- **`kanji.db`** — `kanji(literal, grade, freq, strokes, score)`.

---

## 🧮 Difficulty scoring  (how words are ordered)

Scoring happens **offline** (build step) so runtime comparison is cheap, and is stored in
`entries.score` / `kanji.score`.

1. **Kanji difficulty** (`kanji_score_calculation.py`)
   `kanji_score = 80 × log(freq)/log(2501) + 20 × (grade−1)/9`

2. **Entry (word) difficulty** (`entries_score_calculation.py`) — a blended 100-scale score:
   ```
   word_score = 0.20 × frequency_common  +
                0.20 × avg kanji difficulty +
                0.40 × part-of-speech certainty +
                0.10 × JLPT level
   ```
   Where:
   - `common_sc = 100` or `0` (known/common word).
   - kanji component `= 0.7 × max(kanji_scores) + 0.3 × mean(kanji_scores)` (recent difficult
     kanji weighted most heavily).
   - `pos_sc = 0` if a part of speech is known, `100` otherwise (rare/undiscovered usage is harder).
   - JLPT mapping: `N5:0, N4:25, N3:50, N2:75, N1:100, None:60`.

3. **Ordering** — Word objects are sorted by `SCORE` descending, so **the list top = hardest/most
   interesting words** and the tail is common vocabulary. This `WORD_ORDER` is what the GUI writes.

---

## 📁 Project layout

```
kotoba-lens/
├── .gitignore
├── README.md
└── src/
    ├── main.py              # Entry point for the desktop GUI
    ├── app_context.py       # Bootstrap: OCR model, deinflection rules, DB conn
    ├── ocr.py               # OCRResult dataclass, extract_text(), clean_text(), remove_furigana()
    ├── services.py          # image_process(), import_folder(), add_words_to_DB()
    ├── DAO.py               # Word dataclass + SQL DAOs (add/get)
    ├── gui/
    │   └── image_viewer.py  # ImageViewerApp widget (folder picker, preview, word list)
    ├── parser/
    │   ├── parser.py        # parse() sliding-window dictionary tokenizer
    │   ├── deinflect.py     # BFS de-inflector + apply_rule() + rule loader
    │   └── deinflect_rules.json  # hand-written Japanese morphology rules
    └── database/
        ├── db_config.py     # connect to dictionary.db / kanji.db / main.db
        ├── schema.py        # CREATE TABLE for main.db
        ├── dictionary.db    # JMDict entries (committed)
        ├── kanji.db         # kanji difficulty (committed)
        ├── main.db          # app storage (committed)
        ├── json/
        │   ├── KANJIS.json      # kanji source (~7 MB, tracked)
        │   └── jmdictExtended.json  # JMDict source (~167 MB, git-ignored)
        └── import_script/
            ├── import_jmdict.py            # JSON → dictionary.db
            ├── import_kanji.py            # JSON → kanji.db
            ├── kanji_score_calculation.py # kanji difficulty scores
            └── entries_score_calculation.py # word difficulty scores
```

---

## 🧭 Roadmap / ideas

- [ ] Vocabulary **filters** (restrict to noun / adjective, JLPT level, top-N) — currently word
  list also shows the stored order only.
- [ ] In-GUI re-ranking / score tuning controls.
- [ ] Export reviewed words to Anki / CSV.
- [ ] Properly split `image_viewer` events from the pipeline (OCR currently blocks the Qt thread).

---

## 📄 License

