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
        "footnotes": f_notes  # Stored as metadata
    })

# Step 2: filter pages (skip 1–31 and 390–400). Please see the pdf for more info
pages_and_chunks = [
    item for item in pages_and_chunks_raw
    if item["page_number"] >= 32
    and not (390 <= item["page_number"] <= 400)
    and item["page_number"] != 142
]
doc.close()


#---------------------------------------------------------------------------------------
for i in range(len(pages_and_chunks)-2):  # Stop before the last two
        if not pages_and_chunks[i]["section"] :  # If empty ("" or falsy)
            # Fill from the next one
            pages_and_chunks[i]["section"] = pages_and_chunks[i + 1]["section"]

# Example: Direct index assignment (if pages_and_chunks[0] is page 32) also we skipped pages 390 to 400 so do the math to get exact page numbers
pages_and_chunks[0]["section"] = "Preamble"  # Page 32
pages_and_chunks[24]["section"] = "PART IVA FUNDAMENTAL DUTIES"  # Page 56
pages_and_chunks[250]["section"] = "PART XXII SHORT TITLE, COMMENCEMENT, AUTHORITATIVE TEXT IN HINDI AND REPEALS"  # Page 283
pages_and_chunks[308]["section"] = 'Seventh Schedule' 
pages_and_chunks[325]["section"] = 'Ninth Schedule'
pages_and_chunks[347]["section"] = 'Eleventh Schedule'
pages_and_chunks[348]["section"] = 'Twelfth Schedule'
pages_and_chunks[357]["section"] = "APPENDIX II"  # Page 401
pages_and_chunks[358]["section"] = "APPENDIX III"  # Page 402



#---------------------------------------------------------------------------------------------------
# pages_and_chunks is a list of dicts with keys 'page_number', 'text', 'section'
# Create a dictionary to hold consolidated text by section
consolidated_sections = {}

# Temporary variable to build text for each group
current_section = None
current_text = []
current_page_numbers = []
current_footnotes = {}  # Will be a dict of {page_number: footnotes}

# Iterate through the list of dictionaries (sorted by page_number)
for page in pages_and_chunks:
    section = page['section'].strip()  
    
    if section != current_section:
        # Save the previous group if it exists
        if current_section is not None:
            consolidated_sections[current_section] = {
                "consolidated_text": "\n".join(current_text).strip(),
                "page_numbers": current_page_numbers,  # List of page numbers for this section
                "footnotes": current_footnotes  # Dict of footnotes keyed by page_number
            }
        
        # Start new group
        current_section = section
        current_text = [page['text']]
        current_page_numbers = [page['page_number']]
        current_footnotes = {page['page_number']: page['foot notes']}
    else:
        # Append to current group
        current_text.append(page['text'])
        current_page_numbers.append(page['page_number'])
        current_footnotes[page['page_number']] = page['foot notes']

# Save the last group
if current_section is not None:
    consolidated_sections[current_section] = {
        "consolidated_text": "\n".join(current_text).strip(),
        "page_numbers": current_page_numbers,
        "footnotes": current_footnotes
    }

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

#---------------------------------------------------------------------------------------
chapter_split = []

# Regex pattern to detect chapters - e.g., "CHAPTER I.—GENERAL" or "CHAPTER II.—PARLIAMENT"
chapter_pattern = re.compile(r"^(CHAPTER\s+[IVXLCDM]+\.?—?.*)", re.MULTILINE | re.IGNORECASE)

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

#-------------------------------------------------------------------------------------------------------
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
                chunk = initial_chunk + '\n' + chunk  # Using newline to preserve structure
            
            if chunk:
                article_split.append({'Article number': str(counter)  ,
                                      'text': chunk,
                                      'section': section, 
                                      'chapter': chapter,
                                      'character count':len(chunk) ,
                                      'token count': count_tokens(chunk)})
                
    else:
        # No splits, add the whole text if not empty
        whole_text = consolidated_text.strip()
        if whole_text:
            article_split.append({'Article number':str(counter),
                                  'text': whole_text, 
                                  'section': section, 
                                  'chapter': chapter,
                                  'character count':len(whole_text) ,
                                  'token count': count_tokens(whole_text)})
            

data = article_split[:399]

#------------------------------------------------------------------------------------------------------

import string

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

#-----------------------------------------------------------------------------------------
import re

# Assuming 'sub_article_split' is your list of dictionaries from previous step

# Pattern for clause splits: digit followed by optional spaces and a dot, capturing the digit
# pattern = re.compile(r'(?:\n)?—?\((\d)\)\s*')
pattern = re.compile(r'(\n\(\d+\)\s*)')


# New list for clause level splits
clause_level_split = []

for entry in sub_article_split:
    token_count = entry.get('token_count')  # Assuming token count is present
    text = entry.get('text', '')
    section = entry.get('section')
    chapter = entry.get('chapter')
    article_number = entry.get('Article number')
    sub_article = entry.get('sub-article')
    
    if token_count > 500:
        # Find all split positions, capturing the digit
        splits = [(m.start(), m.group(1)) for m in pattern.finditer(text)]
        
        if splits:
            # Handle initial chunk before first split
            initial_chunk = ''
            first_start = splits[0][0]
            if first_start > 0:
                initial_chunk = text[0:first_start].strip()
            
            for i in range(len(splits)):
                start_pos = splits[i][0]
                end_pos = splits[i + 1][0] if i + 1 < len(splits) else len(text)
                clause_digit = splits[i][1]  # The captured digit
                
                chunk = text[start_pos:end_pos].strip()
                
                # Append initial chunk to the first clause's chunk
                if i == 0 and initial_chunk:
                    chunk = initial_chunk + '\n' + chunk
                
                if chunk:
                    clause_level_split.append({
                        'Article number': article_number,
                        'text': chunk,
                        'section': section,
                        'chapter': chapter,
                        'sub-article': sub_article,
                        'clause': clause_digit,
                        'token_count' : count_tokens(chunk)
                    })
        else:
            # No splits found even though token count > 500, add with clause '0'
            clause_level_split.append({
                'Article number': article_number,
                'text': text,
                'section': section,
                'chapter': chapter,
                'sub-article': sub_article,
                'clause': '0',
                'token_count' :token_count
            })
    else:
        # Token count <= 500 (including <400), add unchanged with clause '0'
        clause_level_split.append({
            'Article number': article_number,
            'text': text,
            'section': section,
            'chapter': chapter,
            'sub-article': sub_article,
            'clause': '0',
            'token_count' : token_count
        })


#-------------------------------------------------------------------------------------------
from sentence_transformers import SentenceTransformer, util
import spacy

# Initialize models

nlp = spacy.load("en_core_web_sm")  # Load spaCy model for sentence segmentation



def sentence_split(text, max_tokens=500):
    """Split large text into sentence-based chunks <= max_tokens using spaCy, with fallback for very long sentences."""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]  # Use spaCy for sentence segmentation
    if not sentences:
        return [text]
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sent in sentences:
        sent_tokens = count_tokens(sent)
        
        # Fallback: If a single sentence exceeds max_tokens, split it on ';'
        if sent_tokens > max_tokens:
            subclauses = [clause.strip() for clause in sent.split(';') if clause]
            #combine the sentences
            for clause in subclauses:
                clause_tokens = count_tokens(clause)
                #if the combination exceeds the token limit, no more combination is possible, append the chunk to the list 
                if current_tokens + clause_tokens > max_tokens and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                current_chunk.append(clause)
                current_tokens += clause_tokens
        else:
            if current_tokens + sent_tokens > max_tokens and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(sent)
            current_tokens += sent_tokens
    
    #for any remaining combinations
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

#-------------------------------------------------------------------------------------------------------------
def merge_consecutive_pairs(chunks, max_tokens=500):
    """Merge consecutive pairs of chunks if their combined token count is < max_tokens. Repeat until no more merges possible. Preserves order."""
    if len(chunks) < 2:
        return chunks

    changed = True
    current_list = chunks[:]

    while changed:
        changed = False
        merged = []
        i = 0
        while i < len(current_list):
            if i == len(current_list) - 1:
                # Last element left as is if odd
                merged.append(current_list[i])
                i += 1
            else:
                first = current_list[i]
                second = current_list[i + 1]
                combined_tokens = first['token_count'] + second['token_count']

                if combined_tokens < max_tokens:
                    # Merge
                    merged_text = first['text'] + ' ' + second['text']
                    merged_dict = {
                        'Article number': first['Article number'],
                        'text': merged_text,
                        'token_count': count_tokens(merged_text),  # Recalculate for accuracy
                        'section': first['section'],
                        'chapter': first['chapter'],
                        
                    }
                    merged.append(merged_dict)
                    changed = True
                    i += 2
                else:
                    merged.append(first)
                    i += 1
        current_list = merged
    return current_list

#-------------------------------------------------------------------------------------------------------------

# Process the data - first do all the sentence level splitting and chunking
post_split_groups = {}  # To hold post-split chunks per article

# Group by article 
article_groups = {}
for item in sub_article_split:
    art_num = item['Article number']
    if art_num not in article_groups:
        article_groups[art_num] = []
    article_groups[art_num].append(item)

for art_num, group in article_groups.items():
    post_split = []
    for item in group:
        if item['token_count'] > 500:
            splits = sentence_split(item['text'])
            for j, split_text in enumerate(splits):
                post_split.append({
                    'Article number': art_num,
                    'text': split_text,
                    'section': item['section'],
                    'chapter': item['chapter'],
                    'sub-article': f"{item['sub-article']}_split{j}",
                    'token_count': count_tokens(split_text)
                })
        else:
            post_split.append(item)
    post_split_groups[art_num] = post_split

# Now apply merging. Note that we are merging only those chunks which belong to the same article
final_chunks = []
for art_num, group_list in post_split_groups.items():
    if group_list:
        merged = merge_consecutive_pairs(group_list)
        final_chunks.extend(merged)

#remove the redundant key
key = 'sub-article'
for d in final_chunks:   # your_list = list of dicts
        d.pop(key, None)   # safely remove key if it exists

#-------------------------------------------------------------------------------------------------------------

def merge_consecutive_pairs2(chunks, max_tokens=500):
    """Merge consecutive pairs of chunks if their combined token count is < max_tokens. Repeat until no more merges possible. Preserves order."""
    if len(chunks) < 2:
        return chunks

    changed = True
    current_list = chunks[:]

    while changed:
        changed = False
        merged = []
        i = 0
        while i < len(current_list):
            if i == len(current_list) - 1:
                # Last element left as is if odd
                merged.append(current_list[i])
                i += 1
            else:
                first = current_list[i]
                second = current_list[i + 1]
                combined_tokens = first['token_count'] + second['token_count']

                if combined_tokens < max_tokens:
                    # Merge
                    merged_text = first['text'] + ' ' + second['text']
                    merged_dict = {
                        'section': first['section'],
                        'text': merged_text,
                        'token_count': count_tokens(merged_text), # Recalculate for accuracy
                        'chapter' : first['chapter']
                    }
                    merged.append(merged_dict)
                    changed = True
                    i += 2
                else:
                    merged.append(first)
                    i += 1
        current_list = merged
    return current_list

#-------------------------------------------------------------------------------------------------------------
chapter_groups = {}
for item in final_chunks:
    #not all sections have chapters so we skip the ones which have chapter None
    if item['chapter'] is not None :
        chapter_num = item['chapter']
        if chapter_num not in chapter_groups:
            chapter_groups[chapter_num] = []
        chapter_groups[chapter_num].append(item)

# merge at section level for those without chapters 
section_groups = {}
for item in final_chunks:
    #we now conside the ones which have chapter None
    if item['chapter'] is None :
        section = item['section']
        if section not in section_groups:
            section_groups[section] = []
        section_groups[section].append(item)


# Now apply chapter-wise article merging
final_chunks_with_chaps = []
for chapter_num, group_list in chapter_groups.items():
    if group_list:
        merged = merge_consecutive_pairs2(group_list)
        final_chunks_with_chaps.extend(merged)

# Now apply section-wise article merging
final_chunks_without_chaps = []
for section, group_list in section_groups.items():
    if group_list:
        merged = merge_consecutive_pairs2(group_list)
        final_chunks_without_chaps.extend(merged)

#merge the two lists 
final_chunks2 = final_chunks_without_chaps + final_chunks_with_chaps

#remove redundant key
key = 'Article number'
for d in final_chunks2:  
        d.pop(key, None)  

final_data = final_chunks2

#removing redundant metadata if any
keys_to_remove = [ 'Article number', 'sub-article']

for d in final_data:   # your_list = list of dicts
    for key in keys_to_remove:
        d.pop(key, None)   # safely remove key if it exists


#--------------------------------------------------------------------------------------------
from sentence_transformers import SentenceTransformer

#i want the model to take 512 i/p tokens
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")


import torch
# Send the model to the GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device) 

# Create embeddings one by one on the GPU - by looping
for item in final_data:
    item["embedding"] = model.encode(item["text"],
                                     normalize_embeddings=True,     # important for cosine/dot
                                     )
    

#faster embedding while done as batches
# Turn text chunks into a single list => this is a list of all sentence chunks
text_chunks = [item["text"] for item in final_chunks2]



# Embed all texts in batches
text_chunk_embeddings = model.encode(text_chunks,
                                               batch_size=32, # you can use different batch sizes here for speed/performance
                                               convert_to_tensor=True,
                                               normalize_embeddings=True,     # important for cosine/dot
                                                )

import pandas as pd
# Save embeddings to file
embeddings_df = pd.DataFrame(final_data)
save_path = "constitution_embeddings.csv"
embeddings_df.to_csv(save_path, index=False)

# Import saved file and view
constitution = pd.read_csv(save_path)
constitution.head()

