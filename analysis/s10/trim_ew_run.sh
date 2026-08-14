#!/usr/bin/env bash
set -e
python3 run_protocol.py "Dail Eireann ewtrim00" perm_ie_ewtrim00 permeation/ie_ewtrim00.jsonl
python3 run_protocol.py "Dail Eireann ewtrim10" perm_ie_ewtrim10 permeation/ie_ewtrim10.jsonl
python3 run_protocol.py "Dail Eireann ewtrim25" perm_ie_ewtrim25 permeation/ie_ewtrim25.jsonl
python3 run_protocol.py "Dail Eireann ewtrim50" perm_ie_ewtrim50 permeation/ie_ewtrim50.jsonl
python3 run_protocol.py "Canada House of Commons ewtrim00" perm_ca_ewtrim00 permeation/ca_ewtrim00.jsonl
python3 run_protocol.py "Canada House of Commons ewtrim10" perm_ca_ewtrim10 permeation/ca_ewtrim10.jsonl
python3 run_protocol.py "Canada House of Commons ewtrim25" perm_ca_ewtrim25 permeation/ca_ewtrim25.jsonl
python3 run_protocol.py "Canada House of Commons ewtrim50" perm_ca_ewtrim50 permeation/ca_ewtrim50.jsonl
python3 run_protocol.py "UK House of Commons ewtrim00" perm_uk_ewtrim00 permeation/uk_ewtrim00.jsonl
python3 run_protocol.py "UK House of Commons ewtrim10" perm_uk_ewtrim10 permeation/uk_ewtrim10.jsonl
python3 run_protocol.py "UK House of Commons ewtrim25" perm_uk_ewtrim25 permeation/uk_ewtrim25.jsonl
python3 run_protocol.py "UK House of Commons ewtrim50" perm_uk_ewtrim50 permeation/uk_ewtrim50.jsonl
