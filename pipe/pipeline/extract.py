"""Auto-generated from DataPreprocessing.ipynb
Module: extract
Notes: Code is preserved as-is (comments added for notebook magics). Cell order is maintained within this module.
Do not edit by hand unless you intend to change the pipeline behavior.
"""


# ===== Notebook Cell 1 =====
import fitz  # PyMuPDF
import re

pdf_path = "constitution of India.pdf"
doc = fitz.open(pdf_path)

# Step 1: raw extraction (all pages) with cleaning and metadata capture
pages_and_chunks_raw = []

for page_num in range(len(doc)):
    text = doc[page_num].get_text("text")
    
    # Remove unwanted lines: headers and standalone digits
    cleaned_lines = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if not re.search(r"THE\s+CONSTITUTION\s+OF\s+INDIA", stripped_line, re.IGNORECASE) and not stripped_line.isdigit():
            cleaned_lines.append(line)
    cleaned_text = "\n".join(cleaned_lines).strip()
    
    # Separate footnotes: look for a line of underscores (e.g., ________________) as separator
    lines = cleaned_text.splitlines()
    main_text_lines = []
    footnotes_lines = []
    in_footnotes = False
    separator_pattern = r'^[_]{5,}$'  # Matches lines with 5 or more underscores (adjust if needed)
    
    for line in lines:
        if re.match(separator_pattern, line.strip()):
            in_footnotes = True
            continue  # Skip the separator line itself
        if in_footnotes:
            footnotes_lines.append(line)
        else:
            main_text_lines.append(line)
    
    # Rebuild main text and footnotes
    main_text = "\n".join(main_text_lines).strip()
    f_notes = "\n".join(footnotes_lines).strip() if footnotes_lines else ""  # Empty if no footnotes
 
    # Now, extract "Section" metadata: look for pattern like "(...)" at the beginning (first few lines) of main_text
    section = ""  # Default to empty if not found
    main_lines = main_text.splitlines()[:5]  # Check only the beginning (first 5 lines)
    section_pattern = r"^\((.+?)\)$"  # Matches lines that are exactly "(content)"
    
    for line in main_lines:
        stripped = line.strip()
        match = re.match(section_pattern, stripped)
        if match:
            section = match.group(1).strip()  # Capture the text inside parentheses
            break  # Stop after finding the first match
    
    # If no match found, ignore (keep as empty) as per query
    
    # Store the page with cleaned main text, footnotes, and metadata
    pages_and_chunks_raw.append({
        "page_number": page_num + 1,
        "text": main_text,
        "section": section,
        "foot notes": f_notes  # Stored as metadata
    })

# Step 2: filter pages (skip 1–31 and 390–400). Please see the pdf for more info
pages_and_chunks = [
    item for item in pages_and_chunks_raw
    if item["page_number"] >= 32
    and not (390 <= item["page_number"] <= 400)
    and item["page_number"] != 142
]
doc.close()

