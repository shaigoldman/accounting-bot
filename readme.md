# Accountant (CSV → categorized monthly exports)

A small CLI tool that ingests credit-card / bank CSV exports (Chase, Citi, Capital One, BoA, Amazon), normalizes them into a common schema, interactively categorizes transactions, and writes one output CSV per month. Built specifically for my personal accounting use.

It also persists description→category decisions so I only categorize new merchants/descriptions over time.

---

## What it does

- Loads all `.csv` files from a target folder (a “batch” folder). (These are downloaded manually from the consumer websites.)
- Detects the source format by filename:
  - `*citi*` or `*cap*` → Citi / Capital One parser
  - `*chase*` → Chase parser
  - `*boa*` → Bank of America parser
  - `*amz*` → Amazon transactions parser
- Normalizes to these columns:

  `["Date", "Description", "Debit", "Credit", "Category", "Og Descript", "Source"]`

- Cleans/desensitizes descriptions (removes punctuation, non-letters, “XX…”, short tokens, state abbrevs, etc.).
- Prompts you (via a terminal dropdown) to assign a category for any **new** cleaned description.
- Writes one CSV of consolidated and labelled transactions per month.
- Saves the category store for future re-use.

### Amazon enrichment

If the filename contains `amz`, the script attempts to replace the transaction description with:

`Amz - <Product Name>`

by matching against Amazon order history using amount and date proximity. Amazon order history can be downloaded from the amazon website.

---

## Requirements

- Python 3.10+
- `pandas`
- `numpy`
- `InquirerPy`

Install dependencies:

```bash
pip install pandas numpy InquirerPy
```

---


## Usage

```bash
python main.py <batch_folder_name>
```

Example:

```bash
python main.py january_upload
```

The script will read:

```
BASE_PATH/january_upload/*.csv
```

and write:

```
OUT_PATH/YYYY-MM.csv
```

---

## Input rules

- Only `.csv` files are processed
- Files starting with `_` are ignored
- Filenames must include one of: `chase`, `citi`, `cap`, `boa`, `amz`
- Unknown formats raise an error

---

## Category store

- Stored as JSON
- Automatically reused across runs
- Only new descriptions trigger prompts

---

## Notes

- Paths are absolute by default (macOS-style).
- Amazon matching is heuristic (amount ± $0.01, date ± 5 days).
- The `delete` category is useful for downstream filtering.

---

## License

Personal / internal use.
