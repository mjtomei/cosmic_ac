#!/usr/bin/env bash
# Frozen protocol on speaker-trimmed corpora.
set -e
python3 run_protocol.py "Dail Eireann trim10" perm_ie_trim10 permeation/ie_trim10.jsonl
python3 run_protocol.py "Dail Eireann trim25" perm_ie_trim25 permeation/ie_trim25.jsonl
python3 run_protocol.py "Canada House of Commons trim10" perm_ca_trim10 permeation/ca_trim10.jsonl
python3 run_protocol.py "Canada House of Commons trim25" perm_ca_trim25 permeation/ca_trim25.jsonl
python3 run_protocol.py "UK House of Commons trim10" perm_uk_trim10 permeation/uk_trim10.jsonl
python3 run_protocol.py "UK House of Commons trim25" perm_uk_trim25 permeation/uk_trim25.jsonl
