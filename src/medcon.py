"""
medcon.py
---------
Implémentation du MEDCON groupé pour l'évaluation de la traduction médicale.

Fonctions exportées :
    - build_pairs(raw_dict)
    - build_automaton(pairs, lang)
    - medcon_grouped(source_en, translation_fr, pairs, automaton_en, automaton_fr)
"""

import ahocorasick


def build_pairs(raw_dict):
    """
    Convertit un dictionnaire {en_term: [fr_terms]} en liste de paires.
    Chaque paire {en, fr} est l'unité atomique du matching groupé.

    Args:
        raw_dict : dict  {str: str | list[str]}

    Returns:
        list of dict  [{en: str, fr: list[str]}, ...]
    """
    pairs = []
    for en_term, fr_variants in raw_dict.items():
        en_clean = en_term.strip().lower()
        if not en_clean:
            continue
        if isinstance(fr_variants, str):
            fr_variants = [fr_variants]
        fr_clean = [t.strip().lower() for t in fr_variants if t.strip()]
        if fr_clean:
            pairs.append({'en': en_clean, 'fr': fr_clean})
    return pairs


def build_automaton(pairs, lang):
    """
    Construit un automate Aho-Corasick pour la langue 'en' ou 'fr'.
    La valeur stockée est l'index de la paire dans `pairs`
    (ou une liste d'indices si un terme est partagé entre plusieurs paires).

    Args:
        pairs : list of dict  (sortie de build_pairs)
        lang  : 'en' | 'fr'

    Returns:
        ahocorasick.Automaton
    """
    A = ahocorasick.Automaton()
    for idx, pair in enumerate(pairs):
        terms = [pair['en']] if lang == 'en' else pair['fr']
        for term in terms:
            if term in A:
                val = A.get(term)
                A.add_word(term, val if isinstance(val, list) else [val, idx])
            else:
                A.add_word(term, idx)
    A.make_automaton()
    return A


def _extract_pair_indices(text, automaton, pairs, lang):
    """
    Retourne l'ensemble des indices de paires dont au moins un terme
    est présent dans `text`, avec vérification des frontières de mots.

    Args:
        text      : str
        automaton : ahocorasick.Automaton
        pairs     : list of dict
        lang      : 'en' | 'fr'

    Returns:
        set of int
    """
    text_lower = text.lower()
    found = set()
    for end_idx, value in automaton.iter(text_lower):
        idx_list = value if isinstance(value, list) else [value]
        for pair_idx in idx_list:
            candidates = [pairs[pair_idx]['en']] if lang == 'en' else pairs[pair_idx]['fr']
            for term in candidates:
                t_start = end_idx - len(term) + 1
                if text_lower[t_start:end_idx + 1] != term:
                    continue
                before_ok = t_start == 0 or not text_lower[t_start - 1].isalnum()
                after_ok  = end_idx + 1 >= len(text_lower) or not text_lower[end_idx + 1].isalnum()
                if before_ok and after_ok:
                    found.add(pair_idx)
                    break
    return found


def medcon_grouped(source_en, translation_fr, pairs, automaton_en, automaton_fr):
    """
    MEDCON groupé : évalue la traduction des termes médicaux par matching de paires EN↔FR.

    Une paire est "attendue" si son terme EN est présent dans la source.
    Une paire est "trouvée"  si au moins un de ses termes FR est présent dans la traduction.
    Une paire est "matchée"  si elle est attendue ET trouvée.

    Scores :
        Precision = |matchée| / |trouvée|
        Recall    = |matchée| / |attendue|
        F1        = harmonic mean(P, R)

    Args:
        source_en      : str  texte source en anglais
        translation_fr : str  traduction française à évaluer
        pairs          : list of dict  (sortie de build_pairs)
        automaton_en   : ahocorasick.Automaton  (lang='en')
        automaton_fr   : ahocorasick.Automaton  (lang='fr')

    Returns:
        dict avec keys : precision, recall, f1, n_expected, n_found, n_match,
                         en_concepts, matched, missed, extra
    """
    expected = _extract_pair_indices(source_en,      automaton_en, pairs, 'en')
    found    = _extract_pair_indices(translation_fr, automaton_fr, pairs, 'fr')

    matched = expected & found
    missed  = expected - found
    extra   = found   - expected

    n_exp, n_found, n_match = len(expected), len(found), len(matched)

    precision = n_match / n_found if n_found > 0 else 0.0
    recall    = n_match / n_exp   if n_exp   > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)

    label = lambda i: f"{pairs[i]['en']} -> {pairs[i]['fr'][0]}"

    return {
        'precision'   : precision,
        'recall'      : recall,
        'f1'          : f1,
        'n_expected'  : n_exp,
        'n_found'     : n_found,
        'n_match'     : n_match,
        'en_concepts' : [pairs[i]['en'] for i in expected],
        'matched'     : [label(i) for i in matched],
        'missed'      : [label(i) for i in missed],
        'extra'       : [label(i) for i in extra],
    }