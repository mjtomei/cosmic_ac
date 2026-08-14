#!/usr/bin/env python3
"""S10 / NL: extract MHA profile prose from archived official House of Assembly
member pages (assembly.nl.ca /members/cms/memberdetail.asp?MemberID=N and
/members/cms/<Name>.htm), fetched via the Internet Archive.

Input : provinces/nl_bio_raw/*.html
Output: provinces/nl_profiles.json  [{file, member_name, district, party, profile}]
"""
import re, html, glob, json, os

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nl_bio_raw')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nl_profiles.json')


def plain(path):
    h = open(path, encoding='utf-8', errors='replace').read()
    h = re.sub(r'<(script|style).*?</\1>', ' ', h, flags=re.S)
    h = re.sub(r'<!--.*?-->', ' ', h, flags=re.S)
    h = re.sub(r'<br\s*/?>', '\n', h, flags=re.I)
    h = re.sub(r'</(p|div|tr|td|h\d|li)>', '\n', h, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', h))
    t = t.replace('\xa0', ' ').replace('�', "'")
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t


def title_name(path):
    h = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'<title>(.*?)</title>', h, flags=re.S | re.I)
    return html.unescape(m.group(1)).strip() if m else ''


def extract(path):
    t = plain(path)
    flat = re.sub(r'\s+', ' ', t)
    i = flat.find('PROFILE')
    prof = ''
    if i >= 0:
        tail = flat[i + len('PROFILE'):].lstrip(': ')
        for stop in ['Back |', 'Home | Copyright', 'Privacy Statement', 'Expense Reports']:
            j = tail.find(stop)
            if j > 0:
                tail = tail[:j]
        prof = tail.strip()
    # member name: text between the nav block end and the district/party line.
    raw = open(path, encoding='utf-8', errors='replace').read()
    name = district = party = ''
    m = re.search(r'<h2>(.*?)</h2>\s*<h3>(.*?)</h3>\s*<h4>(.*?)</h4>', raw, flags=re.S | re.I)
    if m:
        name, district, party = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', g))).strip()
                                 for g in m.groups()]
    if not name:
        m = re.search(r'<h2>(.*?)</h2>', raw, flags=re.S | re.I)
        if m:
            name = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))).strip()
    return {'file': os.path.basename(path), 'member_name': name,
            'district': district, 'party': party,
            'title': title_name(path), 'profile': prof, 'profile_len': len(prof)}


def main():
    recs = [extract(p) for p in sorted(glob.glob(os.path.join(RAW, '*.html')))]
    json.dump(recs, open(OUT, 'w'), indent=1)
    print(len(recs), 'files;', sum(1 for r in recs if r['profile_len'] > 150), 'with profile prose')


if __name__ == '__main__':
    main()
