
# Retrieval-Augmented Generation with the Constitution of India

This project examines the application of Retrieval-Augmented Generation (RAG) to the Constitution of India, integrating traditional information retrieval techniques with modern language models. The system is designed and implemented entirely from scratch in a local environment, ensuring full control over the data pipeline. By eliminating dependence on external APIs, the approach safeguards sensitive legal and policy data, prevents unintended data transfer to third-party services, and promotes reproducibility. The project demonstrates a self-contained framework that can be extended to other legal and governmental corpora for research, education, and policy-support applications.

It demonstrates how raw constitutional text is:  
- Extracted using **PyMuPDF**  
- Cleaned and segmented with **spaCy** into sentence/section-aware chunks  
- Embedded with **SentenceTransformers** (`multi-qa-mpnet-base-dot-v1`)  

These embeddings are stored as **PyTorch tensors** and searched via **CUDA-accelerated similarity operations**.  

For text generation, the system employs **google/gemma-2b-it** via Hugging Face Transformers with **bitsandbytes 4-bit quantization**, enabling efficient inference on limited GPU resources.  

Together, this pipeline produces accurate, **citation-grounded answers** to user queries. The work aims to serve as a foundation for legal and policy assistants, exam preparation tools, and broader applications in structured document retrieval.  

---

## Versions 

### Python: 3.12.9

### PyTorch : 

<img width="455" height="110" alt="image" src="https://github.com/user-attachments/assets/057a83ec-9f7c-465f-834a-4feb066becdd" />


To install, run this inside your venv : 
```bash 
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu129
```

### spaCy Language model: "en_core_web_sm" 

To install, run this inside your venv : 
```bash 
python -m spacy download en_core_web_sm
```

---

## 🚀 How to Run the Pipeline

### 1. Clone the repository
```bash
cd <your repo>
```
```bash
git clone https://github.com/AdarshJyothi/Retrieval-Augmented-Generation-with-Constitution-of-India.git
```


### 2. Set up and activate a virtual environment (recommended)

### 3. Install dependencies
```bash
pip install -r requirements.txt

```

### 4. Ensure project structure
```css
project-root/
├── main.py
├── constitution of India.pdf
└── pipeline/
    ├── __init__.py
    ├── extract.py
    ├── split.py
    ├── chunking.py
    └── embed.py

```

### 5. Run the pipeline

From the project root, execute:
```bash 
python main.py
```

---
    
This will :

* Extract the constitutional text from the provided PDF
* Split into sections, chapters, and articles
* Chunk into manageable token lengths
* Generate embeddings and store them on the GPU for fast similarity search. The embeddings will be saved as `constitution_embeddings_test.csv`


⚠️ Note: The work is still in progress — the complete pipeline will be uploaded soon.
