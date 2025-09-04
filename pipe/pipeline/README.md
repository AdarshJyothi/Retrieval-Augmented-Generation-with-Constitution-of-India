# Modularized Pipeline (Auto-Generated)


## Layout
- `pipeline/extract.py` – PDF/text extraction related cells for constitution.pdf
- `pipeline/split.py` – sentence/token splitting and chunking
- `pipeline/merge.py` – merging of chunks (e.g., `merge_consecutive_pairs`)
- `pipeline/embed.py` – embedding/model related cells
- `pipeline/io.py` – saving/loading data (CSV)
- `pipeline/utils.py` – small helper functions that didn't clearly fit elsewhere
- `pipeline/run.py` – procedural cells in original order, wrapped in `main()`

## How to run
```bash
python -m pipeline.run
```


