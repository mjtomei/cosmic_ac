#!/usr/bin/env bash
# Pull pre-2018 UK Commons debates. The study truncated at 2018 for
# comparability with New Brunswick (the shallowest corpus), not because the
# archive stops there -- ParlParse runs back to 1919. To ask whether the
# secular vocabulary trend predates transformers we need the earlier years.
set -e
cd "$(dirname "$0")"
for y in 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017; do
  rsync -az --include="debates${y}-*.xml" --exclude="*" \
    data.theyworkforyou.com::parldata/scrapedxml/debates/ xml_hist/ 2>&1 \
    | tail -1
  echo "YEAR $y done: $(ls xml_hist/debates${y}-*.xml 2>/dev/null | wc -l) files"
done
touch ../UK_HIST_DONE
