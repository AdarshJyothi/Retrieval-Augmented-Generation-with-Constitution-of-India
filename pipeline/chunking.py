from utils import count_tokens
import spacy
from sentence_transformers import SentenceTransformer, util
# Load spaCy once
nlp = spacy.load("en_core_web_sm")

# i/p : single string(called for strings with token_count > 500)
#function : Sentence level split and merge into chunks with token_count < 500
#o/p : list of strings  
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
    
    return chunks # returns a list of sentences , each with tokens no more than 500.


#i/p : list of strings
#function : Merge consecutive pairs of chunks if their combined token count is < max_tokens. Repeat until no more merges possible. Preserves order.
#o/p : list of dictionaries 

def merge_consecutive_pairs(chunks, max_tokens=500):
    
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


def split_large_texts(data):
    """
    Split texts in the data list where token_count > 500 into smaller chunks.
    Returns a flat list of dictionaries with split texts.
    """
    final_post_split = []
    for d in data:
        if d['token_count'] > 500:
            splits = sentence_split(d['text'])
            for split_text in splits:
                final_post_split.append({
                    'text': split_text,
                    'section': d['section'],
                    'chapter': d['chapter'],
                    'token_count': count_tokens(split_text)
                })
        else:
            final_post_split.append(d.copy())  # Copy to avoid modifying original
    return final_post_split

def group_items(items, by_chapter=True):
    """
    Group items by chapter (if by_chapter=True, skipping chapter '0') or by section (if by_chapter=False, only for chapter '0').
    Returns a dictionary of key (chapter_num or section) to list of items.
    """
    groups = {}
    for item in items:
        if by_chapter:
            if item['chapter'] != "0":
                key = item['chapter']
                groups.setdefault(key, []).append(item)
        else:
            if item['chapter'] == "0":
                key = item['section']
                groups.setdefault(key, []).append(item)
    return groups


def merge_groups(groups):
    """
    Merge consecutive pairs in each group from the input dictionary.
    Returns a flat list of merged dictionaries.
    """
    merged_chunks = []
    for group_list in groups.values():
        if group_list:
            merged = merge_consecutive_pairs(group_list)
            merged_chunks.extend(merged)
    return merged_chunks

def remove_redundant_keys(data, keys_to_remove):
    """
    Remove specified keys from each dictionary in the list.
    Modifies the list in place and returns it.
    """
    for d in data:
        for key in keys_to_remove:
            d.pop(key, None)
    return data


def process_data(data):
    """
    Main function to process the input data:
    - Split large texts
    - Group and merge by chapters and sections
    - Combine results and remove redundant keys
    Returns the final list of dictionaries.
    """
    # Step 1: Split large texts
    split_data = split_large_texts(data)
    
    # Step 2: Group and merge by chapters
    chapter_groups = group_items(split_data, by_chapter=True)
    final_chunks_with_chaps = merge_groups(chapter_groups)
    
    
    # Step 3: Group and merge by sections
    section_groups = group_items(split_data, by_chapter=False)
    final_chunks_without_chaps = merge_groups(section_groups)

    
    # Step 4: Combine and clean
    final_data = final_chunks_without_chaps + final_chunks_with_chaps
    keys_to_remove = ['Article number']
    final_data = remove_redundant_keys(final_data, keys_to_remove)
    
    return final_data

# Example usage:
# final_data = process_data(your_input_data_list)
# print(final_data)