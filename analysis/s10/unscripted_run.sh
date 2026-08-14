#!/usr/bin/env bash
set -e
python3 run_protocol.py "Dail Eireann unscripted" perm_ie_unscripted permeation/ie_unscripted.jsonl
python3 run_protocol.py "Dail Eireann prepared" perm_ie_prepared permeation/ie_prepared.jsonl
python3 run_protocol.py "UK House of Commons unscripted" perm_uk_unscripted permeation/uk_unscripted.jsonl
python3 run_protocol.py "UK House of Commons prepared" perm_uk_prepared permeation/uk_prepared.jsonl
python3 run_protocol.py "Canada House of Commons unscripted" perm_ca_unscripted permeation/ca_unscripted.jsonl
python3 run_protocol.py "Canada House of Commons prepared" perm_ca_prepared permeation/ca_prepared.jsonl
