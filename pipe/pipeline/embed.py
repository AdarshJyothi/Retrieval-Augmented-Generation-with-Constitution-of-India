"""
Module: embed

"""

import torch

# Send the model to the GPU
model.to("cuda") 

# Create embeddings one by one on the GPU - by looping
for item in final_data:
    item["embedding"] = model.encode(item["text"])

# ===== Notebook Cell 74 =====
import pandas as pd
# Save embeddings to file
embeddings_df = pd.DataFrame(final_data)
save_path = "constitution_embeddings.csv"
embeddings_df.to_csv(save_path, index=False)

# ===== Notebook Cell 75 =====
embeddings_df[:3]
