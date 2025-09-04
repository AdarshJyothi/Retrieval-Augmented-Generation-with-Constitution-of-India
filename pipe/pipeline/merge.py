"""Auto-generated from DataPreprocessing.ipynb
Module: merge
Notes: Code is preserved as-is (comments added for notebook magics). Cell order is maintained within this module.
Do not edit by hand unless you intend to change the pipeline behavior.
"""


# ===== Notebook Cell 40 =====
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

# ===== Notebook Cell 50 =====
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
