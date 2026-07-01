"""Extract images from hotel PDFs into assets/hotel-images/

Usage:
  1. Drop your hotel PDFs into assets/pdfs/
  2. Run: python scripts/extract_hotel_images.py

Images land in assets/hotel-images/<hotel-slug>/ and are
automatically picked up by paul_group_dashboard.py.
"""

import fitz  # pip install pymupdf
from pathlib import Path

PDF_MAP = {
    "1. Kumarakom Lake Resort.pdf":       "kumarakom",
    "2. The Paul Bangalore.pdf":           "paul-bangalore",
    "3. Forte Kochi.pdf":                  "forte-kochi",
    "4. Coorg Wilderness Resort & Spa.pdf":"coorg-wilderness",
    "5. Big Banyan Vineyard & Resort.pdf": "big-banyan",
}

BASE = Path(__file__).parent.parent
PDF_DIR = BASE / "assets" / "pdfs"
IMG_DIR = BASE / "assets" / "hotel-images"

MIN_SIZE = 10_000  # skip tiny icons / logos (bytes)


def extract(pdf_path: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    saved = 0
    seen = set()
    for page in doc:
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref in seen:
                continue
            seen.add(xref)
            base = doc.extract_image(xref)
            data = base["image"]
            if len(data) < MIN_SIZE:
                continue
            ext = base["ext"]
            dest = out_dir / f"img_{saved + 1:02d}.{ext}"
            dest.write_bytes(data)
            saved += 1
    return saved


def main():
    print(f"Looking for PDFs in: {PDF_DIR}\n")
    found = 0
    for pdf_name, slug in PDF_MAP.items():
        pdf_path = PDF_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  [skip] {pdf_name} — not found")
            continue
        found += 1
        out = IMG_DIR / slug
        n = extract(pdf_path, out)
        print(f"  [ok]   {pdf_name} -> {n} images -> assets/hotel-images/{slug}/")

    if found == 0:
        print("\nNo PDFs found. Drop them into assets/pdfs/ and re-run.")
    else:
        print(f"\nDone. {found} PDFs processed.")


if __name__ == "__main__":
    main()
