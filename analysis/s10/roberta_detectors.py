#!/usr/bin/env python3
"""S10: supervised-classifier detectors over the corpus.

Three popular free checkpoints:
  - Hello-SimpleAI/chatgpt-detector-roberta  (HC3, 2023)
  - openai-community/roberta-base-openai-detector  (GPT-2 era, 2019)
  - TrustSafeAI/RADAR-Vicuna-7B  (adversarially trained, NeurIPS 2023)
All are RoBERTa-class encoders: fast even on capped clocks. Expected to be
weak/miscalibrated on 2026 text (trained against much older generators) —
included because they are popular, cheap, and candidate Phase-1
stratifiers; calibration on the 2019 control handles the absolute-rate
problem the same way it does for the zero-shot detectors.

The AI-probability index is resolved from each model's id2label (name
containing 'chatgpt'/'fake'/'ai'/'machine'); RADAR's card documents
index 0 = AI-generated.

Output: one CSV per model with p_ai per segment.
Usage: python roberta_detectors.py OUT_PREFIX SEGMENTS_JSONL [...]
"""
import csv
import json
import sys
import time

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODELS = {
    "hc3roberta": "Hello-SimpleAI/chatgpt-detector-roberta",
    "openai_det": "openai-community/roberta-base-openai-detector",
    "radar": "TrustSafeAI/RADAR-Vicuna-7B",
}
BATCH = 64


def ai_index(model, name):
    id2label = {int(k): v.lower() for k, v in
                (model.config.id2label or {}).items()}
    for idx, lab in id2label.items():
        if any(t in lab for t in ("chatgpt", "fake", "ai", "machine")):
            return idx, id2label
    if name == "radar":
        return 0, id2label       # per model card
    return 1, id2label


def main():
    prefix, seg_files = sys.argv[1], sys.argv[2:]
    segs = []
    for pth in seg_files:
        segs += [json.loads(l) for l in open(pth)]
    segs = [s for s in segs if s.get("scoreable")]
    texts = [s["text"] for s in segs]
    print(f"{len(segs)} segments", file=sys.stderr)

    for short, path in MODELS.items():
        t0 = time.perf_counter()
        tok = AutoTokenizer.from_pretrained(path)
        model = AutoModelForSequenceClassification.from_pretrained(
            path, dtype=torch.float32, device_map={"": "cuda:0"}).eval()
        idx, mapping = ai_index(model, short)
        print(f"{short}: id2label={mapping} -> AI index {idx}", flush=True)
        probs = []
        with torch.inference_mode():
            for i in range(0, len(texts), BATCH):
                enc = tok(texts[i:i + BATCH], return_tensors="pt",
                          padding=True, truncation=True,
                          max_length=512).to("cuda:0")
                logits = model(**enc).logits
                probs += F.softmax(logits.float(), -1)[:, idx].cpu().tolist()
        out = f"{prefix}_{short}.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["seg_id", "date", "speaker", "n_words", "orig_frac",
                        "p_ai"])
            for s, p in zip(segs, probs):
                w.writerow([s["seg_id"], s["date"], s["speaker"],
                            s["n_words"], s["orig_frac"], round(p, 6)])
        del model
        torch.cuda.empty_cache()
        print(f"{short}: wrote {out} in {time.perf_counter()-t0:.0f}s",
              flush=True)


if __name__ == "__main__":
    main()
