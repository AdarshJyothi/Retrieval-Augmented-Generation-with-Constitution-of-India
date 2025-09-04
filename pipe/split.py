def split_into_sections(pages):
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
            cur_sec, cur_text, cur_pages, cur_foot = sec, [page["text"]], [
                page["page_number"]
            ], {page["page_number"]: page["footnotes"]}
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


    return sections_list


import re
import string
import spacy
from transformers import AutoTokenizer
TOK = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def count_tokens(text: str) -> int:
    # add_special_tokens ensures model-realistic length
    return len(TOK.encode(text, add_special_tokens=True))



# Note: Requires spaCy model 'en_core_web_sm' to be installed (pip install spacy && python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")


def split_into_chapters(consolidated_sections):
    # Regex pattern to detect chapters - e.g., "CHAPTER I.—GENERAL" or "CHAPTER II.—PARLIAMENT"
    chapter_pattern = re.compile(r"^(CHAPTER\s+[IVXLCDM]+\.?—?.*)", re.MULTILINE | re.IGNORECASE)
    chapter_split = []
    # Iterate over each dictionary in the list (consolidated_sections is list of dicts from previous step)
    for section_dict in consolidated_sections:
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
    data = article_split[:399]
    return data

def split_into_sub_articles(data):
    # New pattern for sub-article splits
    pattern = re.compile(r'\n\s*(\d+[A-Z-]*\.|\d*\[\d+[A-Z-]*\.)')
    # New list for sub-article splits
    sub_article_split = []
    for article in data:
        token_count = article.get('token count', 0)
        text = article.get('text', '')
        section = article.get('section')
        chapter = article.get('chapter', None)
        article_number = article.get('Article number')
        if token_count < 500:
            # Append without splitting, add sub-article '0'
            sub_article_split.append({
                'Article number': article_number,
                'text': text,
                'section': section,
                'chapter': chapter,
                'sub-article': str(0),
                'token_count' : count_tokens(text)
            })
        else:
            # Find splits
            splits = [(m.start(), m.group()) for m in pattern.finditer(text)]
            if splits:
                # Handle initial chunk
                initial_chunk = ''
                first_start = splits[0][0]
                if first_start > 0:
                    initial_chunk = text[0:first_start].strip()
                # Uppercase letters for labeling
                sub_labels = list(string.ascii_uppercase)
                sub_counter = 0
                for i in range(len(splits)):
                    start_pos = splits[i][0]
                    end_pos = splits[i + 1][0] if i + 1 < len(splits) else len(text)
                    chunk = text[start_pos:end_pos].strip()
                    if i == 0 and initial_chunk:
                        chunk = initial_chunk + '\n' + chunk
                    if chunk:
                        sub_label = sub_labels[sub_counter % len(sub_labels)]
                        sub_article_split.append({
                            'Article number': article_number,
                            'text': chunk,
                            'section': section,
                            'chapter': chapter,
                            'sub-article': sub_label,
                            'token_count' : count_tokens(chunk)
                        })
                        sub_counter += 1
            else:
                # No sub-splits found, treat as non-split
                sub_article_split.append({
                    'Article number': article_number,
                    'text': text,
                    'section': section,
                    'chapter': chapter,
                    'sub-article': str(0),
                    'token_count' : count_tokens(text)
                })
    return sub_article_split

# def split_into_clauses(sub_article_split):
#     # Assuming 'sub_article_split' is your list of dictionaries from previous step
#     # Pattern for clause splits: digit followed by optional spaces and a dot, capturing the digit
#     # pattern = re.compile(r'(?:\n)?—?\((\d)\)\s*')
#     pattern = re.compile(r'(\n\(\d+\)\s*)')
#     # New list for clause level splits
#     clause_level_split = []
#     for entry in sub_article_split:
#         token_count = entry.get('token_count')
#         text = entry.get('text', '')
#         section = entry.get('section')
#         chapter = entry.get('chapter')
#         article_number = entry.get('Article number')
#         sub_article = entry.get('sub-article')
#         if token_count > 500:
#             # Find all split positions, capturing the digit
#             splits = [(m.start(), m.group(1)) for m in pattern.finditer(text)]
#             if splits:
#                 # Handle initial chunk before first split
#                 initial_chunk = ''
#                 first_start = splits[0][0]
#                 if first_start > 0:
#                     initial_chunk = text[0:first_start].strip()
#                 for i in range(len(splits)):
#                     start_pos = splits[i][0]
#                     end_pos = splits[i + 1][0] if i + 1 < len(splits) else len(text)
#                     clause_digit = splits[i][1]  # The captured digit
#                     chunk = text[start_pos:end_pos].strip()
#                     # Append initial chunk to the first clause's chunk
#                     if i == 0 and initial_chunk:
#                         chunk = initial_chunk + '\n' + chunk
#                     if chunk:
#                         clause_level_split.append({
#                             'Article number': article_number,
#                             'text': chunk,
#                             'section': section,
#                             'chapter': chapter,
#                             'sub-article': sub_article,
#                             'clause': clause_digit,
#                             'token_count' : count_tokens(chunk)
#                         })
#             else:
#                 # No splits found even though token count > 500, add with clause '0'
#                 clause_level_split.append({
#                     'Article number': article_number,
#                     'text': text,
#                     'section': section,
#                     'chapter': chapter,
#                     'sub-article': sub_article,
#                     'clause': '0',
#                     'token_count' :
