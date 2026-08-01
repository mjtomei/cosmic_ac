#!/usr/bin/env python3
"""S10: prompt-based AI detection against a local OpenAI-compatible server
(vLLM/SGLang container). Same blinded pool and question as all judge trials.

For gpt-oss models, reasoning effort rides the harmony system message
("Reasoning: low|high"), which vLLM's chat template honors.

Usage: python api_prompt_detector.py MODEL MODE OUT_CSV [--limit N] [--port 8000]
"""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

PROMPT = ("Below is an excerpt of transcribed legislative floor speech. "
          "Estimate the probability (0-100) that it was drafted with AI "
          "assistance. Reply with ONLY the integer.\n\n---\n{X}\n---")


def main():
    model, mode, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8000
    url = f"http://127.0.0.1:{port}/v1/chat/completions"

    pool = json.load(open("judge_blind_pool.json"))
    items = sorted(pool.items())
    if limit:
        items = items[:limit]

    def score(item):
        bid, text = item
        is_oss = "gpt-oss" in model
        msgs = ([{"role": "system", "content": f"Reasoning: {mode}"}]
                if is_oss else []) + \
               [{"role": "user", "content": PROMPT.format(X=text)}]
        body = {
            "model": model,
            "messages": msgs,
            "max_tokens": 4096 if mode == "high" else 2048,
            "temperature": 0,
        }
        if not is_oss:
            body["chat_template_kwargs"] = {"enable_thinking": mode == "high"}
        for attempt in range(3):
            try:
                r = requests.post(url, json=body, timeout=600)
                r.raise_for_status()
                msg = r.json()["choices"][0]["message"]
                out = (msg.get("content") or "")
                nums = re.findall(r"\b(\d{1,3})\b", out)
                val = next((int(n) for n in reversed(nums) if int(n) <= 100), None)
                return bid, val, out[-100:].replace("\n", " ")
            except Exception as e:
                if attempt == 2:
                    return bid, None, f"ERR {str(e)[:80]}"
                time.sleep(5)

    t0 = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, res in enumerate(ex.map(score, items), 1):
            results.append(res)
            if i % 40 == 0 or i == len(items):
                print(f"{i}/{len(items)} ({i/(time.perf_counter()-t0):.1f} seg/s)",
                      flush=True)

    with open(out_csv, "w") as f:
        f.write("blind_id,ai_guess,tail\n")
        for bid, val, tail in sorted(results):
            f.write(f'{bid},{val if val is not None else ""},"{tail}"\n')
    ok = sum(1 for _, v, _ in results if v is not None)
    print(f"wrote {out_csv}: {ok}/{len(results)} parsed, "
          f"{time.perf_counter()-t0:.0f}s total", flush=True)


if __name__ == "__main__":
    main()
