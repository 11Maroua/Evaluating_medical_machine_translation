# Evaluating Automatic Translation Quality of Specialized Medical Texts

## Context and Motivation

Automatic translation systems achieve strong general quality today. However, in the
medical domain, they often fail on specialized terms whose exact translation is
critical for clinical understanding. This project evaluates the reliability of
automatic translation of specific medical terms in automatically translated medical
texts, by comparing several systems using a bilingual terminological reference resource.

**Research hypothesis:** Automatic translation is globally reliable for common medical
language, but errors concentrate on specialized technical terms (rare pathologies,
procedure names, abbreviations). Generalist systems correctly translate most text but
struggle on specific medical terminology, while LLMs — trained on larger and more
diverse corpora — should perform better on these specialized terms.

## Approach

We evaluate **GPT-4o** translations of 49 WMT24 biomedical abstracts using three
complementary metrics:

- **BLEU** and **COMET** — standard automatic metrics measuring surface-level fluency
- **MEDCON** — a terminology-aware metric we implement, grounded in a curated
  bilingual MeSH+SNOMED dictionary, that measures how well specialized medical terms
  are translated

We also explore a **RAG-based approach** (Retrieval-Augmented Generation with
dense embeddings + EuroLLM) to improve translation quality on medical terminology,
and assess **LLM-as-a-judge** (MedGemma 4B) as an alternative to automatic metrics.
A subset of translations was manually annotated by a medical doctor to serve as
human reference.

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

## Results

### Notebook 02 — Dictionary Comparison: Why We Use the Cleaned Dictionary

Before evaluating translation quality, we compared the raw and cleaned versions of
the MeSH+SNOMED dictionary to determine which best supports the MEDCON metric.

| | Raw dictionary | Cleaned dictionary |
|---|---|---|
| EN entries | 445,186 | 2,515 |
| Docs with ≥1 expected pair | 49 / 49 | 25 / 49 |
| Avg. expected pairs / doc | 38.43 | 0.82 |
| Precision (valid docs) | 0.494 | 0.820 |
| Recall (valid docs) | 0.450 | 0.760 |
| F1 (valid docs) | 0.463 | 0.780 |
| Unique false positives | 502 | 6 |

The raw dictionary covers all 49 documents but introduces massive noise: generic
words like "on", "study", "between", or mappings like `nursing → soins` and
`2 → deux` are matched as medical terminology, producing 502 unique false positives.
The cleaned dictionary yields a much higher F1 (0.780 vs 0.463) on the documents
it covers, with only 6 false positives.

The Wilcoxon signed-rank test (W=576.0, p=0.716) shows no significant difference
in global F1 scores — explained by the low coverage of the cleaned dictionary
(25/49 docs): on the remaining 24 documents, both dictionaries score 0.0, making
them statistically indistinguishable at corpus level.

**Conclusion:** The cleaned dictionary is retained for all subsequent evaluations.
Its precision and low noise make it a more reliable basis for terminology-aware
evaluation. However, its limited coverage (25/49 docs, 0.82 pairs/doc on average)
is itself a key finding: even a carefully curated 2,515-entry dictionary fails to
cover much of the specialized terminology present in real biomedical corpora.

---

### Notebook 01 — MEDCON Evaluation on GPT-4o

We evaluated GPT-4o translations of 49 WMT24 biomedical abstracts using MEDCON,
BLEU, and COMET.

| Metric | Mean | Std | Min | Max |
|---|---|---|---|---|
| MEDCON F1 | 0.398 | 0.475 | 0.000 | 1.000 |
| BLEU | 49.15 | 12.64 | 18.33 | 79.77 |
| COMET | 0.875 | 0.034 | 0.710 | 0.914 |

**Correlations between metrics:**

| | MEDCON F1 | BLEU | COMET |
|---|---|---|---|
| MEDCON F1 | — | r = +0.071 (p=0.626) | r = −0.029 (p=0.841) |
| BLEU | — | — | r = +0.408 (p=0.004) |

MEDCON is virtually uncorrelated with both BLEU (r=+0.071) and COMET (r=−0.029).
This confirms that MEDCON captures a fundamentally different dimension of translation
quality — terminological accuracy — that standard metrics completely miss. BLEU and
COMET are moderately correlated (r=+0.408), as both measure surface-level fluency.

GPT-4o achieves strong fluency scores (BLEU=49.15, COMET=0.875), but MEDCON reveals
terminology gaps that these metrics ignore. Error analysis on the 25 covered documents
identifies 9 unique missed pairs (e.g. `cardiorespiratory fitness → capacité
cardiorespiratoire`, `antimicrobial stewardship → gestion responsable des
antimicrobiens`) and 6 false positives (e.g. `sadness → tristesse`,
`aftercare → post-cure`).