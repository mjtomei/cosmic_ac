#!/usr/bin/env bash
# Extend the UK series back before the study window. The register is already
# climbing at 2006, our earliest point, so the onset has never been observed.
# ParlParse reaches 1919; 1985 onward is enough to bracket the PC era, the
# consumer-internet era, and a long pre-computer baseline.
set -e
cd "$(dirname "$0")"
for y in $(seq 1985 2005); do
  rsync -az --include="debates${y}-*.xml" --exclude="*" \
    data.theyworkforyou.com::parldata/scrapedxml/debates/ xml_deep/ 2>&1 | tail -1
  echo "YEAR $y: $(ls xml_deep/debates${y}-*.xml 2>/dev/null | wc -l) files"
done
touch ../UK_DEEP_DONE
