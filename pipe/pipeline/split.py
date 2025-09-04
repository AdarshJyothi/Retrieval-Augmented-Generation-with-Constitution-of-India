"""Auto-generated from DataPreprocessing.ipynb
Module: split
Notes: Code is preserved as-is (comments added for notebook magics). Cell order is maintained within this module.
Do not edit by hand unless you intend to change the pipeline behavior.
"""


# ===== Notebook Cell 2 =====
'''this wont affect the section with just 1 page because as per the algorithm, empty section inherits the next section's value. 
since the next page after 1 page section is the first page of the new section, hence empty so the 1 page section inherits this emptiness'''

for i in range(len(pages_and_chunks)-2):  # Stop before the last two
        if not pages_and_chunks[i]["section"] :  # If empty ("" or falsy)
            # Fill from the next one
            pages_and_chunks[i]["section"] = pages_and_chunks[i + 1]["section"]


# ===== Notebook Cell 3 =====
#get the remaining pages with section key empty
empty_pages = []
for item in pages_and_chunks:
        if not item.get("section", "").strip():  # Check if empty or whitespace-only
            empty_pages.append(item["page_number"])

empty_pages

# ===== Notebook Cell 4 =====
pages_and_chunks[109]

# ===== Notebook Cell 5 =====
#since pages 1-32,142,390-400 were removed , need to subtract that many digits to get the current page numbers 
pages_and_chunks[401-11-32-1]["section"] ,pages_and_chunks[402-11-32-1]["section"]  ,pages_and_chunks[358-32-1]["section"] ,pages_and_chunks[341-32-1]["section"]

# ===== Notebook Cell 6 =====
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


# ===== Notebook Cell 8 =====
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

# To preview (example: first section's details)
if consolidated_sections:
    first_sec = list(consolidated_sections.keys())[0]
    print(f"Section: {first_sec}")
    print(f"Page Numbers: {consolidated_sections[first_sec]['page_numbers']}")
    print(f"Footnotes Preview: {list(consolidated_sections[first_sec]['footnotes'].items())[:2]}...")  # First 2 footnotes
    print(f"Text Preview: {consolidated_sections[first_sec]['consolidated_text'][:200]}...\n")

# ===== Notebook Cell 13 =====
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
            "token_count" : len(text)/4,
            
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
                "token_count" : len(chapter_text)/4,
                
            })

# Verify number of splits and some samples
len(chapter_split), chapter_split[:2]


# ===== Notebook Cell 14 =====
chapter_split[:2]

# ===== Notebook Cell 16 =====
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
                                      'token count': len(chunk)/4})
                
    else:
        # No splits, add the whole text if not empty
        whole_text = consolidated_text.strip()
        if whole_text:
            article_split.append({'Article number':str(counter),
                                  'text': whole_text, 
                                  'section': section, 
                                  'chapter': chapter,
                                  'character count':len(whole_text) ,
                                  'token count': len(whole_text)/4})


# ===== Notebook Cell 17 =====
article_split[:2]

# ===== Notebook Cell 19 =====
data = article_split[:399]
data[:2]

# ===== Notebook Cell 26 =====
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
            'token_count' : len(text)/4
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
                        'token_count' : len(chunk)/4
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
                'token_count' : len(text)/4
            })


# ===== Notebook Cell 27 =====
sub_article_split[:2]


# ===== Notebook Cell 28 =====
sub_articles= {}
for item in sub_article_split :
    # if item['token count'] > 400 :
    article = 'Article '+item['Article number']
    sub_article = item['sub-article']
    id  = article+'_' + sub_article
    sub_articles[id] = item['token_count']

# ===== Notebook Cell 33 =====
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
                        'token_count' : len(chunk)/4
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


# ===== Notebook Cell 34 =====
clause_level_split[:5]


# ===== Notebook Cell 35 =====
clauses= {}
for item in clause_level_split :
    # if item['token count'] > 400 :
    article = 'Article '+item['Article number']
    sub_article = item['sub-article']
    clause = item['clause']
    id  = article+'_' + sub_article + '_' + clause
    clauses[id] = item['token_count']

# ===== Notebook Cell 37 =====
import tiktoken
from sentence_transformers import SentenceTransformer, util
import spacy

# ===== Notebook Cell 38 =====
# Initialize models
tokenizer = tiktoken.get_encoding("cl100k_base")  # For token counting
nlp = spacy.load("en_core_web_sm")  # Load spaCy model for sentence segmentation

def count_tokens(text):
    return len(tokenizer.encode(text))

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

# ===== Notebook Cell 41 =====
sub_article_split[:3]

# ===== Notebook Cell 42 =====

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


# ===== Notebook Cell 43 =====
#check if all chunks have token counts less than 500
token_counts= []
for key,value in post_split_groups.items():
    for dict in value :
        token_counts.append(dict['token_count'])
       
print(sorted(token_counts,reverse=True))

# ===== Notebook Cell 45 =====
# Now apply merging. Note that we are merging only those chunks which belong to the same article
final_chunks = []
for art_num, group_list in post_split_groups.items():
    if group_list:
        merged = merge_consecutive_pairs(group_list)
        final_chunks.extend(merged)

# Output or save final_chunks (list of dicts)
print(f"Processed {len(final_chunks)} chunks.")

# ===== Notebook Cell 46 =====
#remove the redundant key
key = 'sub-article'
for d in final_chunks:   # your_list = list of dicts
        d.pop(key, None)   # safely remove key if it exists

# ===== Notebook Cell 47 =====
final_chunks[:2]

# ===== Notebook Cell 48 =====
#check the token counts after merging
token_counts= []
for item in final_chunks:
    token_counts.append(item['token_count'])
    # print(item['token_count'])

print(sorted(token_counts,reverse=True))

# ===== Notebook Cell 51 =====
chapter_groups = {}
for item in final_chunks:
    #not all sections have chapters so we skip the ones which have chapter None
    if item['chapter'] is not None :
        chapter_num = item['chapter']
        if chapter_num not in chapter_groups:
            chapter_groups[chapter_num] = []
        chapter_groups[chapter_num].append(item)

chapter_groups

# ===== Notebook Cell 52 =====

# Now apply chapter-wise article merging
final_chunks_with_chaps = []
for chapter_num, group_list in chapter_groups.items():
    if group_list:
        merged = merge_consecutive_pairs2(group_list)
        final_chunks_with_chaps.extend(merged)

# Output or save final_chunks (list of dicts)
print(f"Processed {len(final_chunks_with_chaps)} chunks.")

# ===== Notebook Cell 54 =====
section_groups = {}
for item in final_chunks:
    #we now conside the ones which have chapter None
    if item['chapter'] is None :
        section = item['section']
        if section not in section_groups:
            section_groups[section] = []
        section_groups[section].append(item)

# section_groups

# ===== Notebook Cell 55 =====
# Now apply chapter-wise article merging
final_chunks_without_chaps = []
for section, group_list in section_groups.items():
    if group_list:
        merged = merge_consecutive_pairs2(group_list)
        final_chunks_without_chaps.extend(merged)

# Output or save final_chunks (list of dicts)
print(f"Processed {len(final_chunks_without_chaps)} chunks.")

# ===== Notebook Cell 56 =====
#merge the two lists 
final_chunks2 = final_chunks_without_chaps + final_chunks_with_chaps
final_chunks2

# ===== Notebook Cell 57 =====
#remove redundant key
key = 'Article number'
for d in final_chunks2:  
        d.pop(key, None)

# ===== Notebook Cell 58 =====
final_chunks2

# ===== Notebook Cell 59 =====
token_counts= []
for item in final_chunks2:
    token_counts.append(item['token_count'])
    # print(item['token_count'])

print(sorted(token_counts,reverse=True))

# ===== Notebook Cell 61 =====
#checking if all the 25 sections are there
chaps = set()
for item in final_chunks2:
    chaps.add(item['section'])
chaps,len(chaps)

# ===== Notebook Cell 63 =====
final_data = final_chunks2

# ===== Notebook Cell 67 =====
from sentence_transformers import SentenceTransformer

#i want the model to take 512 i/p tokens
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")
print(model.max_seq_length)  # should print 512


# ===== Notebook Cell 68 =====
#test
single_sentence = "This is all about the Constitution of India"
single_embedding = model.encode(single_sentence)
print(f"Sentence: {single_sentence}")
print(f"Embedding:\n{single_embedding}")
print(f"Embedding size: {single_embedding.shape}")

# ===== Notebook Cell 72 =====
# %%time

#faster embedding while done as batches
# Turn text chunks into a single list => this is a list of all sentence chunks
text_chunks = [item["text"] for item in final_chunks2]



# Embed all texts in batches
text_chunk_embeddings = model.encode(text_chunks,
                                               batch_size=32, # you can use different batch sizes here for speed/performance, I found 32 works well for this use case
                                               convert_to_tensor=True) # optional to return embeddings as tensor instead of array

text_chunk_embeddings
