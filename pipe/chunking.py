

from transformers import AutoTokenizer
TOK = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def count_tokens(text: str) -> int:
    # add_special_tokens ensures model-realistic length
    return len(TOK.encode(text, add_special_tokens=True))




def merge_consecutive_chunks(chunks, max_tokens=500):
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
                        'chapter': first['chapter']
                    }
                    merged.append(merged_dict)
                    changed = True
                    i += 2
                else:
                    merged.append(first)
                    i += 1
        current_list = merged
    return current_list

def group_and_merge_by_chapter_section(merged_chunks, max_tokens=500):
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
                            'token_count': count_tokens(merged_text),  # Recalculate for accuracy
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
    
    # Process grouping and merging as per original
    chapter_groups = {}
    for item in merged_chunks:
        #not all sections have chapters so we skip the ones which have chapter None
        if item['chapter'] is not None :
            chapter_num = item['chapter']
            if chapter_num not in chapter_groups:
                chapter_groups[chapter_num] = []
            chapter_groups[chapter_num].append(item)
    
    # merge at section level for those without chapters
    section_groups = {}
    for item in merged_chunks:
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
    
    #removing redundant metadata
    keys_to_remove = [ 'Article number', 'sub-article']
    for d in final_chunks2: # your_list = list of dicts
        for key in keys_to_remove:
            d.pop(key, None) # safely remove key if it exists
    
    return final_chunks2
