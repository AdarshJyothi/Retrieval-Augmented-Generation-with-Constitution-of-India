# constitution_pdf_processing.py

def extract_and_clean_pdf_pages(pdf_path):
    import fitz  # PyMuPDF
    import re

    doc = fitz.open(pdf_path)
    pages_and_chunks_raw = []

    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")

        # 1) strip headers / bare-page digits
        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not re.search(r"THE\s+CONSTITUTION\s+OF\s+INDIA", stripped, re.IGNORECASE) and not stripped.isdigit():
                cleaned_lines.append(line)
        cleaned_text = "\n".join(cleaned_lines).strip()

        # 2) split main text vs. foot-notes
        lines = cleaned_text.splitlines()
        main_lines, foot_lines = [], []
        in_footnotes = False
        separator = r'^[_]{5,}$'          # ≥5 underscores
        for ln in lines:
            if re.match(separator, ln.strip()):
                in_footnotes = True
                continue
            (foot_lines if in_footnotes else main_lines).append(ln)

        main_text = "\n".join(main_lines).strip()
        footnotes = "\n".join(foot_lines).strip()

        # 3) grab “(Section …)” metadata (first 5 lines)
        section = ""
        sec_pat = r"^\((.+?)\)$"
        for ln in main_text.splitlines()[:5]:
            m = re.match(sec_pat, ln.strip())
            if m:
                section = m.group(1).strip()
                break

        pages_and_chunks_raw.append(
            dict(
                page_number=page_num + 1,
                text=main_text,
                section=section,
                footnotes=footnotes,
            )
        )
    doc.close()

    pages_and_chunks = [
    item for item in pages_and_chunks_raw
    if item["page_number"] >= 32
    and not (390 <= item["page_number"] <= 400)
    and item["page_number"] != 142
    ]

    for i in range(len(pages_and_chunks)-2):  
        if not pages_and_chunks[i]["section"] :  
            # Fill from the next one
            pages_and_chunks[i]["section"] = pages_and_chunks[i + 1]["section"]

    pages_and_chunks[0]["section"] = "Preamble"  # Page 32
    pages_and_chunks[24]["section"] = "PART IVA FUNDAMENTAL DUTIES"  # Page 56
    pages_and_chunks[250]["section"] = "PART XXII SHORT TITLE, COMMENCEMENT, AUTHORITATIVE TEXT IN HINDI AND REPEALS"  # Page 283
    pages_and_chunks[308]["section"] = 'Seventh Schedule' 
    pages_and_chunks[325]["section"] = 'Ninth Schedule'
    pages_and_chunks[347]["section"] = 'Eleventh Schedule'
    pages_and_chunks[348]["section"] = 'Twelfth Schedule'
    pages_and_chunks[357]["section"] = "APPENDIX II"  # Page 401
    pages_and_chunks[358]["section"] = "APPENDIX III"  # Page 402

    return pages_and_chunks



