import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

def generate_embeddings(final_chunks, model_name="multi-qa-mpnet-base-dot-v1"):
    # Load the model
    model = SentenceTransformer(model_name)
    
    # Send the model to the GPU if available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    # Turn text chunks into a single list
    text_chunks = [item["text"] for item in final_chunks]
    
    # Embed all texts in batches
    text_chunk_embeddings = model.encode(text_chunks,
                                         batch_size=32,
                                         convert_to_tensor=True,
                                         normalize_embeddings=True)
    
    # Assign embeddings back to the dictionaries (convert tensor to numpy for DataFrame compatibility)
    for i, item in enumerate(final_chunks):
        item["embedding"] = text_chunk_embeddings[i].cpu().numpy()
    
    # Create DataFrame
    embeddings_df = pd.DataFrame(final_chunks)
    
    # Save to CSV (as per original)
    save_path = "constitution_embeddings.csv"
    embeddings_df.to_csv(save_path, index=False)
    
    return embeddings_df
