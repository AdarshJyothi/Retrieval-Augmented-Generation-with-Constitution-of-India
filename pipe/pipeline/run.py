"""Orchestration script mirroring the original notebook's procedural flow.
Imports are expected to be present in these blocks as they appeared in the notebook.
Run with:  python -m pipeline.run
"""

def main():
    # The following blocks are literal translations of notebook cells tagged as procedural (no def/class).
    # They execute in the same order as in the notebook.

    # ===== Notebook Cell 9 =====
    #convert consolidated section to a more useable format-list of dictionaries
    sections_list = []
    for section_name, data in consolidated_sections.items():
        text = data["consolidated_text"]
        sections_list.append({
            "section": section_name,
            "consolidated_text": text,
            "section_character_count": len(text),
            "section_token_count": len(text) / 4,
            "page_numbers": data["page_numbers"],
            "footnotes": data["footnotes"]
        })




    




    # ===== Notebook Cell 64 =====
    #removing redundant metadata if any
    keys_to_remove = [ 'Article number', 'sub-article']

    for d in final_data:   # your_list = list of dicts
        for key in keys_to_remove:
            d.pop(key, None)   # safely remove key if it exists

    # ===== Notebook Cell 65 =====
    final_data[:2]

    # ===== Notebook Cell 71 =====
    final_data[:5]


if __name__ == "__main__":
    main()
