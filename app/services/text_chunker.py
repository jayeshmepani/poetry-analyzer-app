from typing import List, Dict, Any


def chunk_words(text: str, chunk_size: int | None = None) -> List[str]:
    words = text.split()
    if not chunk_size or chunk_size <= 0:
        return [text]
    if not words:
        return []
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks


def aggregate_zero_shot(zs, labels: List[str], text: str, chunk_size: int | None = None) -> Dict[str, Any]:
    if not zs or not labels:
        return {"labels": [], "scores": []}
    chunks = chunk_words(text, chunk_size)
    if not chunks:
        return {"labels": [], "scores": []}
    agg: Dict[str, float] = {label: 0.0 for label in labels}
    total = 0
    for chunk in chunks:
        try:
            out = zs(chunk, labels)
            for label, score in zip(out.get("labels", []), out.get("scores", [])):
                agg[label] = agg.get(label, 0.0) + float(score)
            total += 1
        except Exception:
            continue
    if total == 0:
        return {"labels": [], "scores": []}
    # Average scores
    avg = {k: v / total for k, v in agg.items()}
    # Sort labels by score desc
    ordered = sorted(avg.items(), key=lambda x: x[1], reverse=True)
    return {
        "labels": [k for k, _ in ordered],
        "scores": [v for _, v in ordered],
    }
