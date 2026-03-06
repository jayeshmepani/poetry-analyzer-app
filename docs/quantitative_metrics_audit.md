# Quantitative Poetry Metrics Audit

Source: Prompts/quantitative_poetry_metrics.md

## Extraction Checklist (formulas/algorithms)

### Section 2
- [x] Pritchard Scale: Greatness = Perfection × Importance (analysis.py::_pritchard_scale)

### Section 4.1 Prosody & Meter
- [x] Scansion adherence % = (strongly regular lines / total lines) × 100
- [x] Metrical Regularity (heuristic): Sum(match_i)/N with match_i ∈ {0,1} (within ±1 substitution)

### Section 4.1.1 Indic Prosody
- [x] Matra Counting: Laghu=1, Guru=2; conjunct/visarga/anusvara rules
- [x] Matra formula: M(w) = Σ v(s_i) + C(c_i)
- [x] Pingala 8 gana mapping (L/G triplets)
- [x] Chhand verification: IsValidChhand = Σ M(charan_i) == Target_C AND EndRule(C)

### Section 4.1.2 Urdu Aruz
- [x] Taqti algorithm (tokenize → transliterate → syllabify → pattern match → score proportion)

### Section 4.1.3 Gujarati
- [x] Rhyme Density: rhymed endings / total lines OR pairs / pairs

### Section 4.2 Golden Ratio & Fibonacci
- [x] Golden ratio turn position check (phi) (structural_analysis)
- [x] Fibonacci compliance (sequence of line/ syllable counts)

### Section 4.3 Rhyme Scheme
- [x] IsGhazal formula
- [x] Qaafiya density: valid pairs / total couplets (expect 1.0)

### Section 8.1 Lexical Density
- [x] Ld = (Content Words / Total Words) × 100

### Section 8.2 TTR
- [x] TTR = Types / Tokens (and % if required)
- [x] MATTR
- [x] MTLD

### Section 8.3 Readability
- [x] FKGL formula
- [x] FRE formula
- [x] GFI formula
- [x] CLI formula
- [x] ARI formula
- [x] SMOG formula

### Section 8.3.1 Indic Readability
- [x] RH1 = -2.34 + 2.14(AWL) + 0.01(JUK)
- [x] RH2 = -0.82 + 1.83(AWL) + 0.09(PSW)
- [x] MCI = (Total Guru syllables / Total syllables) × 100

### Section 8.5 Chitrakavya
- [x] CSS = 1 - (Violations / Total Constraints)
- [x] Difficulty = log2(valid / total)

### Section 8.4 Info-theoretic
- [x] Perplexity (PPL)
- [x] Entropy of token distribution

### Section 8.5 Embedding novelty
- [x] Novelty = 1 - max(similarity)

### Section 8.7 Computational Greatness
- [x] G_comp = w1*Ld + w2*MTLD + w3*(1-PPL) + w4*N_emb + w5*R_d
- [x] Normalize each metric to [0,1] across comparison set

### Section 14 Practical Formulas
- [x] Lexical Density (token-based) formula
- [x] TTR formula
- [x] Simple Rhyme Density (pairwise)
- [x] Metrical Regularity (Heuristic) formalization

### Section 18 Summary Comparison Table
- [x] All methods in table mapped to implemented modules or rule-based evaluators
