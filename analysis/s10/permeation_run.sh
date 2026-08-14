#!/usr/bin/env bash
# Frozen protocol v1.0, unmodified, per length band.
# Corpus name seeds the RNG, so each band gets its own
# independent placebo draw -- bands are not sharing a null.
set -e
python3 run_protocol.py "New Brunswick short-band" perm_nb_short permeation/nb_short.jsonl
python3 run_protocol.py "New Brunswick long-band" perm_nb_long permeation/nb_long.jsonl
python3 run_protocol.py "Dail Eireann short-band" perm_ie_short permeation/ie_short.jsonl
python3 run_protocol.py "Dail Eireann long-band" perm_ie_long permeation/ie_long.jsonl
python3 run_protocol.py "Canada House of Commons short-band" perm_ca_short permeation/ca_short.jsonl
python3 run_protocol.py "Canada House of Commons long-band" perm_ca_long permeation/ca_long.jsonl
python3 run_protocol.py "UK House of Commons short-band" perm_uk_short permeation/uk_short.jsonl
python3 run_protocol.py "UK House of Commons long-band" perm_uk_long permeation/uk_long.jsonl
