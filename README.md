# Evaluating Automatic Translation Quality of Specialized Medical Texts

This project investigates the reliability of automatic translation systems on
specialized medical terminology. While general-purpose MT systems achieve strong
performance on everyday language, they often fail on domain-specific terms whose
exact translation is critical for clinical understanding.

We evaluate and compare several translation systems — including GPT-4o and a
RAG-based approach — using both standard automatic metrics (BLEU, COMET) and an
adapted terminology-aware metric (MEDCON) grounded in a curated bilingual medical
dictionary. A subset of translations was also evaluated by a medical doctor to
assess correlation between automatic metrics and human clinical judgment.

## Project Structure

```
TER-medical-translation/
├── notebooks/
│   ├── 01_medcon_evaluation.ipynb     # MEDCON + BLEU + COMET on GPT-4o
│   ├── 02_dict_comparison.ipynb       # Cleaned vs uncleaned dictionary comparison
│   ├── 03_doctor_annotations.ipynb    # Correlation with physician annotations
│   ├── 04_rag_embeddings.ipynb        # RAG with embeddings + EuroLLM
│   └── 05_llm_as_judge.ipynb          # LLM-as-a-judge with MedGemma 4B
├── src/
│   ├── medcon.py                      # Grouped MEDCON implementation
│   ├── retrieval.py                   # Embedding-based retrieval
│   └── metrics.py                     # BLEU, COMET wrappers
├── paper/
│   └── paper.pdf                      # Final article
├── results/
└── data/                              # See data/README.md
```

## Data
See [`data/README.md`](data/README.md) for details on the datasets used.