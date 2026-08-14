#!/usr/bin/env bash
set -e
python3 run_protocol.py "Dail Eireann sh00" perm_ie_sh00 permeation/ie_sh00.jsonl
python3 run_protocol.py "Dail Eireann sh10" perm_ie_sh10 permeation/ie_sh10.jsonl
python3 run_protocol.py "Dail Eireann sh25" perm_ie_sh25 permeation/ie_sh25.jsonl
python3 run_protocol.py "Dail Eireann sh50" perm_ie_sh50 permeation/ie_sh50.jsonl
python3 run_protocol.py "Canada House of Commons sh00" perm_ca_sh00 permeation/ca_sh00.jsonl
python3 run_protocol.py "Canada House of Commons sh10" perm_ca_sh10 permeation/ca_sh10.jsonl
python3 run_protocol.py "Canada House of Commons sh25" perm_ca_sh25 permeation/ca_sh25.jsonl
python3 run_protocol.py "Canada House of Commons sh50" perm_ca_sh50 permeation/ca_sh50.jsonl
python3 run_protocol.py "UK House of Commons sh00" perm_uk_sh00 permeation/uk_sh00.jsonl
python3 run_protocol.py "UK House of Commons sh10" perm_uk_sh10 permeation/uk_sh10.jsonl
python3 run_protocol.py "UK House of Commons sh25" perm_uk_sh25 permeation/uk_sh25.jsonl
python3 run_protocol.py "UK House of Commons sh50" perm_uk_sh50 permeation/uk_sh50.jsonl
