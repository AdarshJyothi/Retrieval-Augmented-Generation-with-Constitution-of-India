Retrieval-Augmented Generation with the Constitution of India

The project explores the possibility of Retrieval-Augmented Generation (RAG) applied to the Constitution of India, by combining traditional information retrieval with modern language models.

It demonstrates how raw constitutional text is:

Extracted using PyMuPDF

Cleaned and segmented with spaCy into sentence/section-aware chunks

Embedded with SentenceTransformers (multi-qa-mpnet-base-dot-v1)

These embeddings are stored as PyTorch tensors and searched via CUDA-accelerated similarity operations.

For generation, the system employs google/gemma-2b-it through Hugging Face Transformers with bitsandbytes 4-bit quantization, enabling efficient inference on limited GPU resources.

Together, this pipeline produces accurate, citation-grounded answers to user queries. The work aims to serve as a foundation for legal and policy assistants, exam preparation tools, and broader applications in structured document retrieval.

🚀 How to Run the Pipeline

Clone the repository

git clone https://github.com/AdarshJyothi/Retrieval-Augmented-Generation-with-Constitution-of-India.git
cd Retrieval-Augmented-Generation-with-Constitution-of-India


Set up and activate a virtual environment (recommended)

python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows


Install dependencies

pip install -r requirements.txt


Ensure project structure

project-root/
├── main.py
├── constitution of India.pdf
└── pipeline/
    ├── __init__.py
    ├── extract.py
    ├── split.py
    ├── chunking.py
    └── embed.py


Run the pipeline
From the project root, execute:

python main.py


This will:

Extract the constitutional text from the provided PDF

Split into sections, chapters, and articles

Chunk into manageable token lengths

Generate embeddings and store them on the GPU for fast similarity search

⚠️ The work is still in progress — the complete pipeline will be uploaded soon.
