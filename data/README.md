# Data

## Corpus
The translation corpus is derived from the **WMT24** medical question-answering
dataset. Physician annotations were collected on a separate medical QA dataset
of the same nature.

## Dictionary
The terminology reference is built by merging two standard medical ontologies:
**MeSH** (Medical Subject Headings) and **SNOMED-CT**. Non-medical entries
(geographic locations, food items, etc.) were filtered out, and Zipf's law was
applied to remove overly frequent terms (frequency > 4), yielding the final
curated dictionary `merged_medical_terms_fixed.json`. A smaller filtered version
(`medical_terms_gemini_fixed.json`, ~2,500 entries) was produced using Gemini
as an additional filtering step.