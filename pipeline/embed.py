from sentence_transformers import SentenceTransformer
import torch
import pandas as pd

def load_model(model_name="multi-qa-mpnet-base-dot-v1", device="cuda"):
    """
    Load the SentenceTransformer model and move it to the specified device.
    Returns the loaded model.
    """
    model = SentenceTransformer(model_name)
    model.to(device)
    return model

def add_embeddings_to_data(data, model, batch_size=32):
    """
    Add embeddings to each item in the data list using the provided model.
    Processes in batches for efficiency and normalizes embeddings.
    Modifies the data in place and returns it.
    """
    # Extract texts for batch processing
    texts = [item["text"] for item in data]
    
    # Generate embeddings in batches
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_tensor=True,
        normalize_embeddings=True
    )
    
    # Assign embeddings back to the data (convert tensor to list for CSV compatibility if needed)
    for i, embedding in enumerate(embeddings):
        data[i]["embedding"] = embedding.cpu().tolist()  # Move to CPU and convert to list
    
    return data

def save_embeddings_to_csv(data, save_path="constitution_embeddings.csv"):
    """
    Save the data with embeddings to a CSV file using pandas.
    """
    embeddings_df = pd.DataFrame(data)
    embeddings_df.to_csv(save_path, index=False)
    print(f"Embeddings saved to {save_path}")

def process_data_with_embeddings(final_data, model_name="multi-qa-mpnet-base-dot-v1", device="cuda", batch_size=32, save_path="constitution_embeddings.csv"):
    """
    Extended main function to add embeddings, and save to CSV
    Returns the final data with embeddings.
    """
    # Load model
    model = load_model(model_name, device)
    
    # Add embeddings
    final_data = add_embeddings_to_data(final_data, model, batch_size)
    
    # Save to CSV
    save_embeddings_to_csv(final_data, save_path)
    
    return final_data


