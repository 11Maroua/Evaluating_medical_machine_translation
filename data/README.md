# Data

All data files are excluded from version control (see `.gitignore`).
Statistics were generated via `src/explore_data.py` and are available
in `results/data_stats.json`.

---

## corpus_WMT24.json

Translation corpus derived from the **WMT24** biomedical shared task.
Each document is a medical journal abstract with an English source,
a human French reference translation, and a GPT-4o automatic translation.

| Field | Value |
|---|---|
| Documents | 49 |
| Keys | `doc_id`, `text_en`, `translation_fr`, `gpt_translation` |
| Avg. words (EN) | 189 (min 23 — max 356) |
| Avg. words (FR) | 244 (min 43 — max 468) |

---

## merged_mesh_snomed_dico.json

Raw bilingual terminology dictionary built by merging **MeSH** and **SNOMED-CT**
(English and French versions). Contains the full vocabulary before filtering.

| Field | Value |
|---|---|
| EN entries | 445,186 |
| FR variants per entry (avg) | 1.64 |
| FR variants per entry (max) | 36 |
| Size | 59.0 MB |

---

## cleaned_mesh_snomed_dico.json

Curated version of the merged dictionary. Non-medical entries were removed
(geographic locations, food items, etc.), and Zipf's law was applied to filter
overly frequent terms (frequency > 4). A secondary filtering step using Gemini
was also applied, reducing the dictionary to high-specificity medical terms only.

| Field | Value |
|---|---|
| EN entries | 2,515 |
| FR variants per entry (avg) | 1.48 |
| FR variants per entry (max) | 12 |
| Reduction vs. merged | -99.4% |
| Size | 0.2 MB |

---

## dr_annotations.json

Manual annotations produced by a medical doctor on 25 documents from a medical
QA dataset. Each document was assigned a translation quality score (Likert 1–5)
and flagged for error types when applicable.

| Field | Value |
|---|---|
| Annotated documents | 25 |
| Score average | 4.32 / 5 |
| Score range | 4 — 5 |
| Terminologie incohérente | 21 docs |
| Grammaire / Style | 19 docs |
| Contresens | 1 doc |

---

## unique_contexts_for_RAG.json

French medical text corpus used as retrieval base for the RAG system.
Documents are French abstracts from medical journals, used to provide
in-domain terminology context at translation time.

| Field | Value |
|---|---|
| Documents | 10,995 |
| Avg. words per doc | 213 (min 10 — max 3,142) |
| Size | 15.5 MB |