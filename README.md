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
terminology issues that these metrics completely miss.

Error analysis on the 25 covered documents identifies two types of errors:

- **9 unique missed pairs**: a medical term is present in the English source but its
  French equivalent is absent from the GPT4O-translation (e.g. `cardiorespiratory fitness →
  capacité cardiorespiratoire`, `antimicrobial stewardship → gestion responsable des
  antimicrobiens`). GPT-4o fails to translate these specialized terms correctly.

- **6 unique extras**: a French medical term from the dictionary appears in the
  translation but has no corresponding English term in the source (e.g. `tristesse`,
  `post-cure`). This indicates hallucinations — GPT-4o introduces medical content
  that was not in the original text. This is particularly concerning in a clinical
  context, where a physician reading the translation would encounter symptoms or
  concepts that were never mentioned by the source author. Crucially, these
  hallucinations go completely undetected by BLEU and COMET, which only measure
  surface fluency.

### Notebook 03 — Correlation with Physician Annotations

25 documents were manually annotated by a medical doctor with a translation quality
score (Likert 1–5) and three error types:
- **Inconsistent terminology** (*Terminologie incohérente*): medical terms translated
  inconsistently or inaccurately across the document
- **Grammar / Style** (*Grammaire / Style*): unnatural phrasing, grammatical errors,
  or register issues
- **Mistranslation** (*Contresens*): semantic errors that alter the meaning of the
  original text

**Physician score distribution:**

| Score | Docs |
|---|---|
| 4/5 | 17 (68%) |
| 5/5 | 8 (32%) |
| **Mean** | **4.32/5** |

**Error type distribution:**

| Error type | Docs | % |
|---|---|---|
| Inconsistent terminology | 21 | 84% |
| Grammar / Style | 19 | 76% |
| Mistranslation | 1 | 4% |
| No error | 4 | 16% |

The physician's assessment reveals that GPT-4o produces translations that are
globally satisfactory — all scores are 4 or 5 out of 5, with no document rated
below 4. This suggests that the overall meaning and structure of the medical texts
are well preserved. However, the high rate of terminology (84%) and style (76%)
issues indicates that translations, while clinically intelligible, lack the
naturalness and precision expected in a professional medical context. The near-absence
of mistranslations (4%) confirms that GPT-4o rarely alters the core meaning of the
source text, but consistently produces output that a medical professional would
find awkward or imprecise in terminology.

**Correlation with automatic metrics:**

| Metric | Mean | Pearson r | p-val | Spearman ρ | p-val |
|---|---|---|---|---|---|
| MEDCON F1 | 0.428 | +0.157 | 0.452 | +0.134 | 0.524 |
| COMET-QE | 0.198 | −0.138 | 0.511 | −0.143 | 0.496 |
| mBERT similarity | 0.851 | +0.255 | 0.218 | +0.202 | 0.333 |
| Sentence-BERT | 0.912 | −0.087 | 0.679 | −0.131 | 0.533 |

No metric correlates significantly with the physician score (all p > 0.05). mBERT
shows the highest Pearson correlation (r=+0.255) but remains far from significance.
COMET-QE and Sentence-BERT even show negative correlations due to very surfacic evaluation of the MT.

These results are explained by two main factors: the annotated corpus is small (n=25),
and physician scores are concentrated in a very narrow range (4–5 out of 5), which
drastically reduces variance and makes any correlation statistically difficult to
detect. Furthermore, the physician evaluates overall clinical quality, while automatic
metrics measure more formal aspects (terminology, semantic similarity, fluency).
This absence of correlation motivates the exploration of a **LLM-as-a-judge** approach
(notebook 05), where a medically specialized model (MedGemma 4B) is used to evaluate
translation quality in a way closer to human clinical reasoning.

### Notebook 04 — RAG with Embeddings + Mistral API

We implement a RAG-based translation system to improve medical terminology accuracy:
- **Retrieval**: dense embeddings (`intfloat/multilingual-e5-base`) + FAISS index
  over 10,995 French medical abstracts (`unique_contexts_for_RAG.json`)
- **Generation**: `mistral-small-latest` via Mistral API, prompted with the top-3
  most semantically similar French contexts (k=3)

| System | MEDCON F1 | BLEU |
|---|---|---|
| GPT-4o | 0.398 | 49.15 |
| RAG (Mistral + Embeddings, k=3) | 0.414 | 49.58 |

The RAG system produces marginal improvements over GPT-4o (+0.016 MEDCON F1,
+0.43 BLEU), with **47 out of 49 documents showing identical scores**.

These results are best interpreted as a limitation of the evaluation metrics rather
than a failure of the RAG approach. BLEU and MEDCON operate on exact string matching
and are fundamentally insensitive to subtle improvements in terminology naturalness,
register, or phrasing precision — precisely the dimensions that RAG is designed to
improve. Two translations can differ meaningfully in medical quality while producing
identical BLEU and MEDCON scores.

Furthermore, Mistral is already a strong medical translator out of the box, trained
on large multilingual corpora that include substantial medical content. When the base
model already produces fluent, accurate translations, in-context examples from a RAG
system provide limited additional signal — there is little room for improvement that
these metrics can detect.

This motivates the LLM-as-a-judge approach explored in notebook 05, where MedGemma 4B
— a model specifically trained on medical data — evaluates translation quality beyond
surface-level metrics, assessing clinical accuracy, terminology consistency, and
naturalness in a way that BLEU and MEDCON cannot.

### Notebook 05 — LLM-as-a-Judge with MedGemma 4B

We use MedGemma 4B — a model specifically trained on medical data — as an automatic
judge to evaluate translation quality beyond surface-level metrics. For each
translation, MedGemma assigns a Likert score from 1 to 5 based on medical accuracy,
terminology consistency, and fluency.

**GPT-4o vs RAG Mistral — MedGemma scores:**

| System | Mean score | Std | Min | Max |
|---|---|---|---|---|
| GPT-4o | 3.33/5 | 1.13 | 2 | 5 |
| RAG (Mistral + Embeddings) | 3.45/5 | 1.11 | 2 | 5 |

| Score | GPT-4o | RAG |
|---|---|---|
| 2/5 | 17 | 14 |
| 3/5 | 8 | 9 |
| 4/5 | 15 | 16 |
| 5/5 | 9 | 10 |

MedGemma rates RAG slightly higher than GPT-4o (3.45 vs 3.33), confirming the
marginal improvement observed with MEDCON and BLEU. The RAG system scores higher
on 13/49 documents, lower on 10/49, and equal on 26/49 — consistent with the
near-identical performance observed in notebook 04.

Notably, MedGemma's scores are substantially lower than the physician's (3.33–3.45
vs 4.32/5). MedGemma appears more critical of translation quality, penalizing
terminology and fluency issues that the physician — evaluating clinical acceptability
— considered minor.

**Correlation with automatic metrics (GPT-4o, n=49):**

| Metric | Pearson r | p-val | Spearman ρ | p-val |
|---|---|---|---|---|
| MEDCON F1 | +0.043 | 0.767 | +0.042 | 0.774 |
| BLEU | −0.305 | 0.033 | −0.233 | 0.107 |

MedGemma is uncorrelated with MEDCON (r=+0.043), confirming that they measure
different dimensions. The negative correlation with BLEU (r=−0.305, p=0.033) is
significant and counter-intuitive: documents where GPT-4o achieves high BLEU tend
to receive lower MedGemma scores. This suggests that surface-level fluency, as
measured by BLEU, does not reflect medical translation quality — a high BLEU score
can coexist with poor clinical accuracy.

**Correlation with physician annotations (n=25):**

| | Mean score | Pearson r | p-val | Spearman ρ | p-val |
|---|---|---|---|---|---|
| Physician | 4.32/5 | — | — | — | — |
| MedGemma | 3.96/5 | +0.046 | 0.828 | +0.008 | 0.970 |

MedGemma does not correlate with the physician's judgment (r=+0.046, p=0.828).
Both evaluate on a 1–5 scale but capture different aspects: the physician assesses
clinical acceptability in context, while MedGemma evaluates formal translation
quality without clinical grounding. The low variance in physician scores (all 4–5)
further limits statistical detectability, as discussed in notebook 03.

**Conclusion:** MedGemma provides a more critical and differentiated evaluation than
BLEU or COMET, and its negative correlation with BLEU is a meaningful finding —
fluency and medical accuracy are not the same thing. However, its lack of correlation
with physician judgment suggests that even a medically specialized LLM judge cannot
fully replicate human clinical evaluation. The combination of MEDCON (terminology),
BLEU (fluency), and MedGemma (medical quality judgment) provides a more complete
picture than any single metric alone.