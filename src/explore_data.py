"""
explore_data.py
Génère les statistiques descriptives de tous les fichiers de données.
Lancer depuis la racine du projet : python3 src/explore_data.py
"""

import json
import os

DATA_DIR = 'data'

files = {
    'corpus_WMT24'   : 'corpus_WMT24.json',
    'merged_dico'    : 'merged_mesh_snomed_dico.json',
    'cleaned_dico'   : 'cleaned_mesh_snomed_dico.json',
    'dr_annotations' : 'dr_annotations.json',
    'rag_contexts'   : 'unique_contexts_for_RAG.json',
}

stats = {}

# ── corpus WMT24 ──────────────────────────────────────────────
with open(os.path.join(DATA_DIR, files['corpus_WMT24'])) as f:
    wmt = json.load(f)

en_lens = [len(d['text_en'].split()) for d in wmt]
fr_lens = [len(d.get('translation_fr', '').split()) for d in wmt]

stats['corpus_WMT24'] = {
    'n_docs'        : len(wmt),
    'keys'          : list(wmt[0].keys()),
    'en_avg_words'  : round(sum(en_lens) / len(en_lens)),
    'en_min_words'  : min(en_lens),
    'en_max_words'  : max(en_lens),
    'fr_avg_words'  : round(sum(fr_lens) / len(fr_lens)),
    'fr_min_words'  : min(fr_lens),
    'fr_max_words'  : max(fr_lens),
}

# ── merged dico ───────────────────────────────────────────────
with open(os.path.join(DATA_DIR, files['merged_dico'])) as f:
    merged = json.load(f)

fr_counts = [len(v) if isinstance(v, list) else 1 for v in merged.values()]
stats['merged_dico'] = {
    'n_entries'         : len(merged),
    'fr_variants_avg'   : round(sum(fr_counts) / len(fr_counts), 2),
    'fr_variants_max'   : max(fr_counts),
    'size_mb'           : round(os.path.getsize(os.path.join(DATA_DIR, files['merged_dico'])) / 1024 / 1024, 1),
}

# ── cleaned dico ──────────────────────────────────────────────
with open(os.path.join(DATA_DIR, files['cleaned_dico'])) as f:
    cleaned = json.load(f)

fr_counts_c = [len(v) if isinstance(v, list) else 1 for v in cleaned.values()]
stats['cleaned_dico'] = {
    'n_entries'         : len(cleaned),
    'fr_variants_avg'   : round(sum(fr_counts_c) / len(fr_counts_c), 2),
    'fr_variants_max'   : max(fr_counts_c),
    'reduction_pct'     : round(100 * (1 - len(cleaned) / len(merged)), 1),
    'size_mb'           : round(os.path.getsize(os.path.join(DATA_DIR, files['cleaned_dico'])) / 1024 / 1024, 1),
}

# ── doctor annotations ────────────────────────────────────────
with open(os.path.join(DATA_DIR, files['dr_annotations'])) as f:
    ann = json.load(f)

scores, error_types = [], []
for doc in ann:
    if not doc['annotations']:
        continue
    for r in doc['annotations'][0]['result']:
        if r['from_name'] == 'translation_likert':
            scores.append(int(r['value']['choices'][0]))
        elif r['from_name'] == 'document_issue_types':
            error_types.extend(r['value']['choices'])

from collections import Counter
stats['dr_annotations'] = {
    'n_docs'        : len(ann),
    'score_avg'     : round(sum(scores) / len(scores), 2) if scores else None,
    'score_min'     : min(scores) if scores else None,
    'score_max'     : max(scores) if scores else None,
    'error_types'   : dict(Counter(error_types)),
}

# ── RAG contexts ──────────────────────────────────────────────
with open(os.path.join(DATA_DIR, files['rag_contexts'])) as f:
    rag = json.load(f)

rag_lens = [len(str(c).split()) for c in rag]
stats['rag_contexts'] = {
    'n_docs'        : len(rag),
    'avg_words'     : round(sum(rag_lens) / len(rag_lens)),
    'min_words'     : min(rag_lens),
    'max_words'     : max(rag_lens),
    'size_mb'       : round(os.path.getsize(os.path.join(DATA_DIR, files['rag_contexts'])) / 1024 / 1024, 1),
}

# ── Affichage ─────────────────────────────────────────────────
for name, s in stats.items():
    print(f'\n{"="*50}')
    print(f'  {name}')
    print(f'{"="*50}')
    for k, v in s.items():
        print(f'  {k:<20} : {v}')

# ── Export JSON ───────────────────────────────────────────────
os.makedirs('results', exist_ok=True)
with open('results/data_stats.json', 'w') as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print('\n\nStats exportées dans results/data_stats.json')