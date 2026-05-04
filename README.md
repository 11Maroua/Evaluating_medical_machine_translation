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
struggle on specific medical terminology, while LLMs trained on larger and more
diverse corpora should perform better on these specialized terms.

## Approach

We evaluate **GPT-4o** translations of 49 WMT24 biomedical abstracts using three
complementary metrics:

- **BLEU** — measures n-gram overlap between a candidate translation and a human
  reference translation. Score ranges from 0 to 100.
- **COMET** — a score produced by a neural model trained to predict translation
  quality by comparing a candidate translation to a human reference. Score typically
  ranges from 0 to 1.
- **MEDCON-like** — a terminology-aware metric we implement, grounded in a curated
  bilingual MeSH+SNOMED dictionary, that measures the proportion of medical terms
  present in the source that are correctly translated in the output. F1 score between
  0 and 1.
- **LLM-as-a-judge** (MedGemma 4B) — a medically specialized model that assigns a
  Likert score (1-5) to evaluate translation quality.

We also explore a **RAG-based approach** (Retrieval-Augmented Generation with dense
embeddings + Mistral API) as a method to improve translation quality on medical
terminology. A subset of translations was manually annotated by a medical doctor
to serve as human reference.

## Project Structure
```
TER-medical-translation/
├── notebooks/
│   ├── 01_medcon_evaluation.ipynb     # MEDCON + BLEU + COMET on GPT-4o
│   ├── 02_dict_comparison.ipynb       # Cleaned vs uncleaned dictionary comparison
│   ├── 03_doctor_annotations.ipynb    # Correlation with physician annotations
│   ├── 04_rag_embeddings.ipynb        # RAG with embeddings using Mistral
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

See [`data/README.md`](data/README.md) for details. Key files:

| File | Description |
|---|---|
| `corpus_WMT24.json` | 49 biomedical abstracts (EN source, human FR ref, GPT-4o translation) |
| `merged_mesh_snomed_dico.json` | Raw MeSH+SNOMED bilingual dictionary (445,186 EN entries) |
| `cleaned_mesh_snomed_dico.json` | Curated dictionary after Zipf filtering + Gemini (2,515 EN entries) |
| `dr_annotations.json` | Manual annotations by a medical doctor (25 documents, Likert 1-5) |
| `unique_contexts_for_RAG.json` | 10,995 French medical abstracts used as RAG retrieval corpus |

---

## Results

### Evaluation Metrics

#### Notebook 02: Dictionary Comparison

Before evaluating translation quality, we compared the raw and cleaned versions of
the MeSH+SNOMED dictionary to determine which best supports the MEDCON-like metric.

| | Raw dictionary | Cleaned dictionary |
|---|---|---|
| EN entries | 445,186 | 2,515 |
| Docs with >=1 expected pair | 49 / 49 | 25 / 49 |
| Avg. expected pairs / doc | 38.43 | 0.82 |
| Precision (valid docs) | 0.494 | 0.820 |
| Recall (valid docs) | 0.450 | 0.760 |
| F1 (valid docs) | 0.463 | 0.780 |
| Unique false positives | 502 | 6 |

The raw dictionary covers all 49 documents but introduces massive noise: generic
words like "on", "study", "between", or mappings like `nursing -> soins` and
`2 -> deux` are matched as medical terminology, producing 502 unique false positives.
The cleaned dictionary shows a higher F1 on the documents it covers (0.780 vs 0.463)
and only 6 false positives. However, this difference should be interpreted with
caution: a smaller dictionary will mechanically yield higher precision and F1 scores
on the pairs it covers, which does not necessarily imply better overall quality.
The cleaned dictionary is selected for subsequent evaluations primarily because of
its substantially lower noise level.

---

#### Notebook 01: MEDCON-like Evaluation on GPT-4o

We evaluated GPT-4o translations of 49 WMT24 biomedical abstracts using MEDCON-like,
BLEU, and COMET.

| Metric | Mean | Std | Min | Max |
|---|---|---|---|---|
| MEDCON-like F1 | 0.398 | 0.475 | 0.000 | 1.000 |
| BLEU | 49.15 | 12.64 | 18.33 | 79.77 |
| COMET | 0.875 | 0.034 | 0.710 | 0.914 |

**Correlations between metrics:**

| | MEDCON-like F1 | BLEU | COMET |
|---|---|---|---|
| MEDCON-like F1 | | r = +0.071 (p=0.626) | r = -0.029 (p=0.841) |
| BLEU | | | r = +0.408 (p=0.004) |

MEDCON-like is virtually uncorrelated with both BLEU (r=+0.071) and COMET (r=-0.029),
suggesting it captures a different dimension of translation quality. BLEU and COMET
are moderately correlated (r=+0.408). Both metrics compare a candidate translation
to a human reference, but through different mechanisms: BLEU via n-gram overlap and
COMET via a learned neural similarity model.

Error analysis on the 25 covered documents identifies two types of errors:

- **9 unique missed pairs**: a medical term is present in the English source but its
  French equivalent is absent from the GPT-4o translation (e.g. `cardiorespiratory
  fitness -> capacite cardiorespiratoire`, `antimicrobial stewardship -> gestion
  responsable des antimicrobiens`).

- **6 unique extras**: a French medical term from the dictionary appears in the
  translation but has no corresponding English term in the source (e.g. `tristesse`,
  `post-cure`). This may indicate hallucinations where GPT-4o introduces medical
  content not present in the original text, though MEDCON-like matching alone is
  insufficient to confirm this without manual verification.

---

#### Notebook 03:  Correlation with Physician Annotations

25 documents were manually annotated by a medical doctor on MedGemma-27B translations
with a quality score (Likert 1-5) and three error types:
- **Inconsistent terminology** (*Terminologie incoherente*): medical terms translated
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

**Error type distribution:**

| Error type | Docs | % |
|---|---|---|
| Inconsistent terminology | 21 | 84% |
| Grammar / Style | 19 | 76% |
| Mistranslation | 1 | 4% |
| No error | 4 | 16% |

The physician's assessment reveals that MedGemma-27B produces translations that are
globally satisfactory, with all scores at 4 or 5 out of 5. However, the high rate
of terminology (84%) and style (76%) issues indicates that translations, while
clinically intelligible, lack the naturalness and precision expected in a professional
medical context.

**Correlation with automatic metrics:**

| Metric | Pearson r | p-val | Spearman rho | p-val |
|---|---|---|---|---|
| MEDCON-like F1 | +0.157 | 0.452 | +0.134 | 0.524 |
| COMET-QE | -0.138 | 0.511 | -0.143 | 0.496 |
| mBERT similarity | +0.255 | 0.218 | +0.202 | 0.333 |
| Sentence-BERT | -0.087 | 0.679 | -0.131 | 0.533 |

No metric correlates significantly with the physician score (all p > 0.05). These
results are explained by two main factors: the annotated corpus is small (n=25), and
physician scores are concentrated in a very narrow range (4-5 out of 5), which
drastically reduces variance and makes any correlation statistically difficult to
detect.

### Corrélation point-bisériale : Erreur terminologique vs MedTerm F1
The binary terminology error flag (0/1) is correlated with MEDCON-like F1 using the
point-biserial correlation, and here are the results: 

| Statistique | Valeur |
|---|---|
| n | 25 |
| Docs avec erreur terminologie | 21 / 25 |
| Point-bisériale r | +0,179 |
| p-valeur | 0,391 |
| MedTerm F1 moyen (avec erreur) | 0,462 |
| MedTerm F1 moyen (sans erreur) | 0,250 |

> Résultat non significatif (p ≥ 0,05). La corrélation est positive mais la taille réduite du sous-ensemble annoté (n=25) limite la détectabilité de tout effet.


---

#### Notebook 05: LLM-as-a-Judge with MedGemma 4B
We use MedGemma 4B (loaded in bfloat16, without quantization) as an automatic judge
to evaluate translation quality. For each translation, MedGemma assigns a Likert
score from 1 to 5 based on medical accuracy, terminology consistency, and naturalness.

**GPT-4o — MedGemma scores (n=49):**

| Mean | Std | Min | Max |
|---|---|---|---|
| 3.96/5 | 0.20 | 3 | 4 |

MedGemma rates GPT-4o translations in a very narrow range (3 to 4 out of 5), with
low variance (std=0.20). This limited score distribution makes correlation analysis
with other metrics difficult to interpret.

**Correlation with automatic metrics (GPT-4o, n=49):**

| Metric | Pearson r | p-val | Spearman rho | p-val |
|---|---|---|---|---|
| MEDCON-like F1 | -0.045 | 0.760 | -0.046 | 0.755 |
| BLEU | -0.019 | 0.895 | -0.029 | 0.842 |

Neither MEDCON-like nor BLEU correlates with MedGemma scores (all p > 0.05).

**Correlation with physician annotations (n=25):**

| | Mean score | Pearson r | p-val | Spearman rho | p-val |
|---|---|---|---|---|---|
| Physician | 4.32/5 | | | | |
| MedGemma | 4.04/5 | +0.298 | 0.149 | +0.298 | 0.149 |

MedGemma does not correlate significantly with the physician's judgment (p=0.149),
though the direction is now positive (r=+0.298) and closer to significance than
in the quantized version (r=+0.046). The score distribution is highly concentrated:
MedGemma assigns 4/5 to 24 out of 25 documents and 5/5 to only 1, while the
physician assigned 4/5 to 17 and 5/5 to 8. Both evaluators agree on the general
quality level but MedGemma is less willing to assign the highest score.

---

### Translation Methods

#### Notebook 04:  Mistral vs Mistral + RAG

We compare two translation approaches using the same base model (`mistral-small-latest`):
- **Mistral**: direct translation with a simple instruction prompt
- **Mistral + RAG**: same model, but the prompt includes the top-3 most semantically
  similar French medical abstracts retrieved via dense embeddings
  (`intfloat/multilingual-e5-base`) + FAISS over 10,995 French medical abstracts (k=3)

| System | MEDCON-like F1 | BLEU |
|---|---|---|
| Mistral | 0.439 | 48.14 |
| Mistral + RAG (k=3) | 0.435 | 49.08 |

The two systems produce near-identical results: RAG shows a marginal BLEU improvement
(+0.94) but a negligible MEDCON-like decrease (-0.004), with 48 out of 49 documents
receiving identical scores on both metrics.

Qualitative analysis reveals that on most documents, Mistral and Mistral+RAG produce
nearly identical translations. The one document where RAG degrades MEDCON-like most
(doc #12, delta=-0.200) is a COVID-19 vaccination study where the RAG translation
introduces a `**Résumé :**` header not present in the source, a formatting artifact
inherited from the retrieved contexts. On BLEU however this same document scores
slightly higher with RAG (54.3 vs 52.9).
These results confirm that when the base model is already a strong translator,
retrieved contexts provide little additional signal. The absence of measurable
improvement should be interpreted in light of the metrics used: both BLEU and
MEDCON-like rely on exact matching and are insensitive to subtle differences in
phrasing or register that RAG is designed to improve.