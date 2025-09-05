# extract.py
import re
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF


_HEADER_RE = re.compile(r"THE\s+CONSTITUTION\s+OF\s+INDIA", re.IGNORECASE)
_SECTION_LINE_RE = re.compile(r"^\((.+?)\)$")  # e.g., "(PART IV—DIRECTIVE PRINCIPLES...)"
_FOOTNOTE_SEP_RE_DEFAULT = re.compile(r"^[_]{5,}$")  # line of 5+ underscores
_STANDALONE_DIGITS_RE = re.compile(r"^\d+$")


def _clean_and_split(text: str, footnote_sep_re: re.Pattern) -> tuple[str, str]:
    """Remove headers/standalone digits, then split main text vs footnotes."""
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if _HEADER_RE.search(s):
            continue
        if _STANDALONE_DIGITS_RE.match(s):
            continue
        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).strip()
    lines = cleaned_text.splitlines()

    main_text_lines: List[str] = []
    footnotes_lines: List[str] = []
    in_footnotes = False

    for line in lines:
        if footnote_sep_re.match(line.strip()):
            in_footnotes = True
            continue
        (footnotes_lines if in_footnotes else main_text_lines).append(line)

    main_text = "\n".join(main_text_lines).strip()
    footnotes = "\n".join(footnotes_lines).strip()
    return main_text, footnotes


def _detect_section(main_text: str, probe_lines: int = 5) -> str:
    """Look for a line like '(PART ...)' in the first few lines."""
    for line in main_text.splitlines()[:probe_lines]:
        m = _SECTION_LINE_RE.match(line.strip())
        if m:
            return m.group(1).strip()
    return ""


def extract_pages(
    pdf_path: str,
    *,
    page_min: int = 32,  # keep from this inclusive
    skip_ranges: Optional[List[Tuple[int, int]]] = None,  # inclusive ranges
    skip_pages: Optional[List[int]] = None,               # explicit page_numbers to skip
    # footnote_separator_regex: str = r"^[_]{5,}$", #use this incase a different pattern is needed
) -> List[Dict]:
    """
    Extract cleaned pages with metadata:
    returns list of dicts with keys: page_number, text, section, footnotes

    Tips:
      - Prefer passing `manual_section_labels` with real PDF page numbers.
      - Avoid brittle index-based overrides.
    """
    if skip_ranges is None:
        skip_ranges = [(390, 400)]  # inclusive
    if skip_pages is None:
        skip_pages = [142]

    # Build a set of pages to skip
    skip_set = set(skip_pages)
    for a, b in skip_ranges:
        skip_set.update(range(a, b + 1))

    # footnote_sep_re = re.compile(footnote_separator_regex)
    footnote_sep_re = _FOOTNOTE_SEP_RE_DEFAULT
    pages: List[Dict] = []
    with fitz.open(pdf_path) as doc:
        for i in range(len(doc)):
            page_number = i + 1  # human-readable page number
            if page_number < page_min:
                continue
            if page_number in skip_set:
                continue

            raw_text = doc[i].get_text("text")
            main_text, footnotes = _clean_and_split(raw_text, footnote_sep_re)
            section = _detect_section(main_text)

            pages.append(
                {
                    "page_number": page_number,
                    "text": main_text,
                    "section": section,
                    "footnotes": footnotes,  # consistent key name
                }
            )

    # Fill empty sections from the next page's section
    for i in range(len(pages) - 2):  # Stop before the last two
        if not pages[i]["section"]:
            pages[i]["section"] = pages[i + 1]["section"]

    # Manual overrides by index (using list index, not page_number)
    pages[0]["section"] = "Preamble"  # Page 32
    pages[24]["section"] = "PART IVA FUNDAMENTAL DUTIES"  # Page 56
    pages[250]["section"] = "PART XXII SHORT TITLE, COMMENCEMENT, AUTHORITATIVE TEXT IN HINDI AND REPEALS"  # Page 283
    pages[308]["section"] = "Seventh Schedule"
    pages[325]["section"] = "Ninth Schedule"
    pages[347]["section"] = "Eleventh Schedule"
    pages[348]["section"] = "Twelfth Schedule"
    pages[357]["section"] = "APPENDIX II"  # Page 401
    pages[358]["section"] = "APPENDIX III"  # Page 402

    return pages

#for testing
if __name__ == "__main__":
    result = extract_pages("constitution of India.pdf")
    with open("pages.txt", "w", encoding="utf-8") as f:
        for item in result:
            for key, value in item.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")  # blank line between dictionaries
    

