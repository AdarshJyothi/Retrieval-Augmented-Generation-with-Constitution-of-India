import re
import string
import spacy

from utils import count_tokens



def split_into_sections(pages):
    """Group page dicts into sections, merging text, page numbers, and footnotes."""
    consolidated = {}
    cur_sec, cur_text, cur_pages, cur_foot = None, [], [], {}

    for page in pages:
        sec = page["section"].strip()
        if sec != cur_sec:
            if cur_sec is not None:
                consolidated[cur_sec] = dict(
                    consolidated_text="\n".join(cur_text).strip(),
                    page_numbers=cur_pages,
                    footnotes=cur_foot,
                )
            # reset trackers
            cur_sec, cur_text, cur_pages, cur_foot = sec, [page["text"]], [page["page_number"]], {page["page_number"]: page["footnotes"]}
        else:
            cur_text.append(page["text"])
            cur_pages.append(page["page_number"])
            cur_foot[page["page_number"]] = page["footnotes"]

    # save last bucket
    if cur_sec is not None:
        consolidated[cur_sec] = dict(
            consolidated_text="\n".join(cur_text).strip(),
            page_numbers=cur_pages,
            footnotes=cur_foot,
        )

    sections_list = []
    for section_name, data in consolidated.items():
        text = data["consolidated_text"]
        sections_list.append({
            "section": section_name,
            "consolidated_text": text,
            "section_character_count": len(text),
            "section_token_count": count_tokens(text),
            "page_numbers": data["page_numbers"],
            "footnotes": data["footnotes"]
        })

    return sections_list



def split_into_chapters(sections_list):
    # Regex pattern to detect chapters - e.g., "CHAPTER I.—GENERAL" or "CHAPTER II.—PARLIAMENT"
    chapter_pattern = re.compile(r"^(CHAPTER\s+[IVXLCDM]+\.?—?.*)", re.MULTILINE | re.IGNORECASE)
    chapter_split = []
    # Iterate over each dictionary in the list (sections_list is list of dicts from previous step)
    for section_dict in sections_list:
        section_name = section_dict['section']
        text = section_dict['consolidated_text']
        # Find all chapter matches and their positions
        matches = list(chapter_pattern.finditer(text))
        if not matches:
            # No chapters found - keep the section as is
            chapter_split.append({
                'section': section_name,
                'chapter': None,
                'consolidated_text': text,
                "character_count" : len(text),
                "token_count" : count_tokens(text),
            })
        else:
            # Chapters found - split text into chapter chunks
            for i, match in enumerate(matches):
                start_pos = match.start()
                end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                chapter_text = text[start_pos:end_pos].strip()
                chapter_title = match.group(1).strip()
                
                chapter_split.append({
                    'section': section_name,
                    'chapter': chapter_title,
                    'consolidated_text': chapter_text,
                    "character_count" : len(chapter_text),
                    "token_count" : count_tokens(chapter_text),
                })
    return chapter_split



def split_into_articles(chapter_split):
    # Regex pattern for splits
    pattern = re.compile(r'\n\s*(\d+\.|\d*\[\d+\.)')

    # New list for article splits
    article_split = []

    # Global counter starting from 1- this is to preserve the article number as some articles have sub-articles like 51A, Counter both gets the number 51 .
    counter = 0

    # Iterate over each dictionary in the list
    for entry in chapter_split:
        section = entry.get('section')
        chapter = entry.get('chapter')
        consolidated_text = entry.get('consolidated_text', '')

        # Find all split positions
        splits = [(m.start(), m.group()) for m in pattern.finditer(consolidated_text)]

        # If there are splits
        if splits:
            initial_chunk = ''#to get the data before the first split if any
            # Check for initial chunk before first split
            first_start = splits[0][0]
            if first_start > 0:
                initial_chunk = consolidated_text[0:first_start].strip()

            # Now handle the split chunks
            for i in range(len(splits)):
                counter+= 1
                # Skip 238 if reached- this was omitted from the constitution and that page was removed during the data extraction phase
                if counter == 238:
                    counter += 1
                start_pos = splits[i][0]
                end_pos = splits[i + 1][0] if i + 1 < len(splits) else len(consolidated_text)
                chunk = consolidated_text[start_pos:end_pos].strip()
                # Append initial chunk to the first split's chunk
                if i == 0 and initial_chunk:
                    chunk = initial_chunk + '\n' + chunk # Using newline to preserve structure
                if chunk:
                    article_split.append({'Article number': str(counter) ,
                                           'text': chunk,
                                           'section': section,
                                           'chapter': chapter,
                                           'character count':len(chunk) ,
                                           'token count': count_tokens(chunk)})

        else: # No splits, add the whole text if not empty
            whole_text = consolidated_text.strip()
            if whole_text:
                article_split.append({'Article number':str(counter),
                                      'text': whole_text,
                                      'section': section,
                                      'chapter': chapter,
                                      'character count':len(whole_text) ,
                                      'token count': count_tokens(whole_text)})

    data = article_split[:399]#excluding the schedules and and appendices -again specific to this pdf
    return data




