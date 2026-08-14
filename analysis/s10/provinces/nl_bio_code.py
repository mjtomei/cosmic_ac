#!/usr/bin/env python3
"""S10 / NL: code the official archived MHA profiles into education / occupation fields,
and join them to the NL members in provinces/member_bios.json.

Coding was done by reading each profile's PROFILE prose (see nl_profiles.json).
Every value below is attested in that prose; "unknown" means the official
biography does not state it. Nothing here comes from Wikipedia.

Output: provinces/nl_education_occupation.json
"""
import json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

# name -> (education_level, education_field, [alma_maters], prior_occupation, occupation_category)
CODE = {
 "Allan Hawkins": ("bachelor","","Memorial University of Newfoundland","career in education and business; Mayor","unknown"),
 "Andrew Parsons": ("professional","law","","lawyer (called to the NL bar 2005)","law"),
 "Barry Petten": ("college","business management and accounting","College of the North Atlantic|Memorial University of Newfoundland","mental health counsellor (20 years); executive assistant to ministers","health"),
 "Bernard Davis": ("bachelor","commerce","Memorial University of Newfoundland","executive director and program coordinator, Church Lads' Brigade; city councillor","NGO-advocacy"),
 "Betty Parsley": ("college","travel and tourism","","travel consultant (20+ years); mayor","business"),
 "Bob Ridgley": ("graduate","education","Iona College|Memorial University of Newfoundland","teacher, principal and school board supervisor (18 years); business (13 years)","education"),
 "Brian Warr": ("college","police sciences","Memorial University of Newfoundland|Holland College","Royal Newfoundland Constabulary officer; manager of family hardware business","business"),
 "Calvin Peach": ("secondary","","St. Francis Xavier University","fish plant worker; FFAW union representative and organizer; harbour supervisor/administrator","trades-labour"),
 "Carol Anne Haley": ("unknown","","","special assistant to an MP; community service officer/coordinator in economic development","public-service"),
 "Cathy Bennett": ("unknown","","Institute of Corporate Directors","CEO, Bennett Group of Companies","business"),
 "Charlene Johnson": ("graduate","engineering","University of New Brunswick|Memorial University of Newfoundland","consultant; employed with a regulatory agency working with electric and water utilities","public-service"),
 "Christopher Mitchelmore": ("bachelor","commerce","Memorial University of Newfoundland","client services officer, Community Business Development Corporation Nortip","business"),
 "Clayton Forsey": ("college","architectural drafting","","draftsman, Iron Ore Company of Canada; sales/accounting, Morgan Printing; divisional supervisor, Brookfield Dairy","business"),
 "Clyde Jackman": ("graduate","education","Memorial University of Newfoundland|Mount Saint Vincent University","teacher and school principal (27 years)","education"),
 "Colin Holloway": ("bachelor","","Memorial University of Newfoundland","provincial public service (26 years)","public-service"),
 "Dale Kirby": ("graduate","education","Memorial University of Newfoundland|University of Toronto","professor, Faculty of Education, Memorial University; senior education policy advisor, Ontario Public Service","education"),
 "Dan Crummell": ("bachelor","political science","Memorial University of Newfoundland","sales and marketing, Molson Canada (25 years)","business"),
 "Darin T. King": ("graduate","education","Memorial University of Newfoundland|Saint Mary's University|Northcentral University","CEO/Director of Education, Eastern School District; teacher","education"),
 "Darryl Kelly": ("graduate","education","Memorial University of Newfoundland","teacher and school administrator (30 years)","education"),
 "Dave Denine": ("bachelor","education","Memorial University of Newfoundland","teacher","education"),
 "David Brazil": ("bachelor","","Memorial University of Newfoundland|College of the North Atlantic|York University","senior manager, provincial government (26 years); independent business owner","public-service"),
 "Derek Bennett": ("college","community recreation leadership","College of Trades and Technology","director of recreation and tourism, Town of Lewisporte (25 years)","public-service"),
 "Derrick Bragg": ("unknown","","","town clerk/manager, Greenspond (30 years)","public-service"),
 "Derrick Dalley": ("graduate","education","Memorial University of Newfoundland|University of New Brunswick","social worker; guidance counsellor and school principal","education"),
 "Dianne Whalen": ("unknown","","","employed at College of the North Atlantic (29 years); mayor of Paradise","unknown"),
 "Dwight Ball": ("professional","pharmacy","Memorial University of Newfoundland","pharmacist","health"),
 "Ed Buckingham": ("graduate","education","Memorial University of Newfoundland","teacher","education"),
 "Eddie Joyce": ("unknown","","","","unknown"),
 "Eli Cross": ("unknown","","","teacher, vice-principal and principal (31-year education career)","education"),
 "Elizabeth (Beth) Marshall": ("professional","accounting","Memorial University of Newfoundland","Auditor General of Newfoundland and Labrador; deputy minister; chartered accountant","public-service"),
 "Felix Collins": ("professional","law","Memorial University of Newfoundland|Boston University|University of Ottawa","school principal, teacher and superintendent of education; then lawyer (1996-2007)","law"),
 "George Murphy": ("college","public relations","","co-founder, Consumer Group for Fair Gas Prices","NGO-advocacy"),
 "Gerry Byrne": ("bachelor","science","Dalhousie University","Member of Parliament (1996-2015)","public-service"),
 "Gerry Rogers": ("bachelor","social work","Memorial University of Newfoundland","documentary filmmaker; women's advocacy worker","communications-PR-journalism"),
 "Glen Little": ("college","electrical and carpentry; human resources and labour relations","College of the North Atlantic","26 years in the public health care sector; NAPE local president","health"),
 "Glenn Littlejohn": ("bachelor","education","Memorial University of Newfoundland","provincial public service (recreation and sport, historic sites, youth services) from 1987","public-service"),
 "Graham Letto": ("unknown","","Memorial University of Newfoundland","30-year career with the Iron Ore Company of Canada; mayor of Labrador City","unknown"),
 "Harry Harding": ("college","","Gander District Vocational School|Memorial University of Newfoundland","labourer and fish plant worker; teacher (2 years); payroll clerk; town clerk/manager (15 years); resource manager, Beothic Fish Processors (14 years)","business"),
 "Jack Byrne": ("college","surveying technology","College of Trades and Technology|Memorial University of Newfoundland","land surveyor; president of survey companies","business"),
 "Jerome Kennedy": ("professional","law","Memorial University of Newfoundland|University of New Brunswick","criminal lawyer","law"),
 "Jerry Dean": ("secondary","","","careers with Clarke Transport, Crosbie Offshore, Abitibi and the Department of Finance","public-service"),
 "Jim Baker": ("college","business administration","Memorial University of Newfoundland","senior business analyst, Iron Ore Company of Canada","business"),
 "Jim Bennett": ("professional","law","Memorial University of Newfoundland|University of Windsor|University of Detroit Mercy","","unknown"),
 "Joan Burke": ("graduate","social work","Memorial University of Newfoundland|University of Toronto","parole officer, Correctional Service of Canada","public-service"),
 "Joan Shea": ("graduate","social work","Memorial University of Newfoundland|University of Toronto","parole officer, Correctional Service of Canada","public-service"),
 "John Dinn": ("bachelor","education","Memorial University of Newfoundland","teacher (29 years); landscaping business owner","education"),
 "John Finn": ("college","community studies","College of the North Atlantic","employment counsellor and housing/homelessness caseworker, Community Education Network","NGO-advocacy"),
 "John Haggie": ("professional","medicine","","general surgeon","health"),
 "John Hickey": ("college","high voltage lineman","College of the North Atlantic","25 years with Newfoundland and Labrador Hydro, including senior management","trades-labour"),
 "Kathy Dunderdale": ("unknown","","Memorial University of Newfoundland","worked in community development, communications, fisheries and social work","other"),
 "Keith Hutchings": ("bachelor","political science","Memorial University of Newfoundland|Ryerson University","11 years with the Workplace Health, Safety and Compensation Commission; chief of staff to the Leader of the Opposition; consultant","public-service"),
 "Keith Russell": ("bachelor","business administration","St. Francis Xavier University","","unknown"),
 "Kelvin Parsons": ("professional","law","Memorial University of Newfoundland|University of New Brunswick","lawyer (practised at Port aux Basques 1980-1999)","law"),
 "Kevin O'Brien": ("professional","pharmacy","","pharmacist; owner, O'Brien's Pharmacy and Medical Centre","health"),
 "Kevin Parsons": ("college","electronics","College of the North Atlantic","IKON Office Solutions (27 years)","business"),
 "Kevin Pollard": ("bachelor","physical education","Memorial University of Newfoundland","teacher (28 years)","education"),
 "Lisa Dempster": ("college","tourism","Memorial University of Newfoundland","career and employment counsellor (23 years)","other"),
 "Lorraine Michael": ("bachelor","","Memorial University of Newfoundland|University of Toronto","high school teacher and principal; Director, Office of Social Action; Executive Director, Women in Resource Development Committee","NGO-advocacy"),
 "Mark Browne": ("bachelor","political science","Memorial University of Newfoundland","aide to a Member of Parliament; political assistant, Official Opposition","public-service"),
 "Neil King": ("bachelor","marine engineering technology","Memorial University of Newfoundland|Marine Institute","officer, Royal Canadian Navy (14 years)","public-service"),
 "Nick McGrath": ("unknown","","","businessman; owned and operated six businesses in Labrador West","business"),
 "Pam Parsons": ("bachelor","political science","Mount Saint Vincent University|Nova Scotia Community College","reporter and producer (CBC, Rogers TV, NTV)","communications-PR-journalism"),
 "Patty Pottle": ("bachelor","education","Memorial University of Newfoundland","teacher (6 years); entrepreneur (gift shop, property company, inn)","business"),
 "Paul Davis": ("college","police studies","Holland College","police officer, Royal Newfoundland Constabulary","public-service"),
 "Paul Lane": ("unknown","","","career in occupational health and safety","other"),
 "Paul Oram": ("college","business management","","construction company owner; funeral director and funeral home owner","business"),
 "Perry Trimper": ("bachelor","forestry and wildlife management","","principal scientist, Stantec (resource development, land use, wildlife ecology)","other"),
 "Randy Edmunds": ("secondary","","","fisherman and boat captain; weather observer; environmental observer, Labrador Inuit Association; hotel and tourism owner","business"),
 "Ray Hunter": ("college","electrical trades","","owner-operator, Hunter's Electrical Ltd. (journeyman electrician)","trades-labour"),
 "Roger Fitzgerald": ("unknown","","","","unknown"),
 "Roland Butler": ("college","business administration","","executive assistant to MHAs","public-service"),
 "Ross Wiseman": ("unknown","","","15-year career in health administration; financial services management","health"),
 "Sam Slade": ("college","fisheries (Fishing Master Class IV)","Fisheries and Marine Institute","fishing enterprise owner-operator","agriculture"),
 "Sandy Collins": ("bachelor","political science and education","Memorial University of Newfoundland","teacher; constituency assistant and executive assistant to ministers","public-service"),
 "Scott Reid": ("graduate","education and political science","Memorial University of Newfoundland|University of Ottawa","provincial public service (Director of Communications, Director of Research); university lecturer; community newspaper owner","public-service"),
 "Shawn Skinner": ("college","applied arts; adult education","Memorial University of Newfoundland|Cabot College|St. Francis Xavier University","instructor, faculty supervisor, principal and operator, Keyin College (20 years)","education"),
 "Sheila Osborne": ("unknown","","","secretary and office manager, government and private sector","other"),
 "Sherry Gambin-Walsh": ("college","nursing","Memorial University of Newfoundland","neonatal nurse; executive director, NL Association for Community Living","health"),
 "Siobhan Coady": ("unknown","","Memorial University of Newfoundland|University of Oxford|University of Toronto","business owner and CEO (biotechnology, fisheries, resources); Member of Parliament","business"),
 "Steve Crocker": ("unknown","","","executive assistant to the Leader of the Opposition; entrepreneur in family business","public-service"),
 "Steve Kent": ("graduate","business and management","Memorial University of Newfoundland|McGill University","CEO, Big Brothers Big Sisters of Eastern Newfoundland; management and marketing consultant; business owner","business"),
 "Susan Sullivan": ("graduate","education","Memorial University of Newfoundland|Mount Saint Vincent University|Universite Laval","teacher (30-year career)","education"),
 "Terry French": ("secondary","","Memorial University of Newfoundland","executive assistant to a Member of Parliament (1997-2002); family business","public-service"),
 "Terry Loder": ("college","insurance","","insurance adjuster (32 years)","business"),
 "Tom Hedderson": ("graduate","education and psychology","Memorial University of Newfoundland|Mount Saint Vincent University","school principal","education"),
 "Tom Marshall": ("professional","law","Memorial University of Newfoundland|Dalhousie University","lawyer, senior partner in a Corner Brook law firm","law"),
 "Tom Osborne": ("college","","Cabot College|Memorial University of Newfoundland","Statistics Canada (1986-1990); Small Business Enterprise; Penney Group of Companies","business"),
 "Tom Rideout": ("professional","law","University of Ottawa","high school teacher and vice-principal (before entering politics in 1975); later lawyer","law"),
 "Tony Cornect": ("college","","College of the North Atlantic","experience in media, economic development and sales; political assistant to an MHA","other"),
 "Tracey Perry": ("bachelor","commerce","Memorial University of Newfoundland","consultant (TMP Consulting Inc.); Executive Director, Coast of Bays Corporation regional economic development board","other"),
 "Trevor Taylor": ("unknown","","","fisherman and boat skipper; staff member, Fish, Food and Allied Workers union","agriculture"),
 "Vaughn Granter": ("graduate","education","Memorial University of Newfoundland|St. Francis Xavier University","teacher and school principal","education"),
 "Wade Verge": ("graduate","education and mathematics","Memorial University of Newfoundland","teacher and school principal (22 years)","education"),
 "Wallace Young": ("unknown","","Memorial University of Newfoundland","co-owner, Plum Point Motel","business"),
 "Yvonne Jones": ("college","","West Viking College","journalist and news reporter; owner-operator of small businesses in transportation and tourism","business"),
 "Danny Williams": ("professional","law","Memorial University of Newfoundland|University of Oxford|Dalhousie University","lawyer; founder of Cable Atlantic","business"),
}

# Surname-only speaker keys in member_bios.json that are unambiguous for their date span.
MANUAL = {
 "burke": "Joan Burke",
 "osborne": "Tom Osborne",
 "collins": "Felix Collins",
 "forsey": "Clayton Forsey",
 "parsons": "Kelvin Parsons",
 "hawkins": "Allan Hawkins",
 "littlejohn": "Glenn Littlejohn",
 "e. marshall": "Elizabeth (Beth) Marshall",
}
# Surname-only keys that span two or more different members: left unknown on purpose.
AMBIGUOUS = {"reid","king","byrne","sullivan","dean","dinn","davis"}


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z ]', '', s).strip()


def main():
    prof = json.load(open(os.path.join(HERE, 'nl_profiles.json')))
    best = {}
    for x in prof:
        if x['profile_len'] < 150:
            continue
        n = re.sub(r',.*', '', x['member_name']).strip()
        if n not in best or x['profile_len'] > best[n]['profile_len']:
            best[n] = x
    # archived source url per file
    def src(fn):
        m = re.match(r'md_(\d+)_(\d{4})\.html', fn)
        if m:
            return ('https://web.archive.org/web/%s/http://www.assembly.nl.ca/members/cms/'
                    'memberdetail.asp?MemberID=%d' % (m.group(2), int(m.group(1))))
        m = re.match(r'nm_([A-Za-z]+)_(\d{8})\.html', fn)
        if m:
            return ('https://web.archive.org/web/%s/http://www.assembly.nl.ca/members/cms/%s.htm'
                    % (m.group(2), m.group(1)))
        return ''

    pmap = {norm(k): k for k in best}
    targets = [r for r in json.load(open(os.path.join(HERE, 'member_bios.json')))
               if r.get('prov') == 'NL']
    out, unmatched = [], []
    for r in targets:
        key = None
        for c in (r.get('matched_name'), r['name']):
            if c and norm(c) in pmap:
                key = pmap[norm(c)]
                break
        if key is None and r['name'] in MANUAL:
            key = MANUAL[r['name']]
        rec = {'name': key or r.get('matched_name') or r['name'], 'speaker_key': r['name'],
               'first_seen': r['first_seen'], 'last_seen': r['last_seen']}
        if key is None:
            rec.update(education_level='unknown', education_field='', alma_maters=[],
                       prior_occupation='', occupation_category='unknown', source_url='',
                       matched_profile=None)
            unmatched.append(r['name'])
        else:
            lvl, fld, alma, occ, cat = CODE[key]
            rec.update(education_level=lvl, education_field=fld,
                       alma_maters=[a for a in alma.split('|') if a],
                       prior_occupation=occ, occupation_category=cat,
                       source_url=src(best[key]['file']), matched_profile=key)
        out.append(rec)
    json.dump(out, open(os.path.join(HERE, 'nl_education_occupation.json'), 'w'), indent=1)
    n_ed = sum(1 for x in out if x['education_level'] != 'unknown')
    n_oc = sum(1 for x in out if x['occupation_category'] != 'unknown')
    print('members', len(out), 'matched', len(out) - len(unmatched),
          'education', n_ed, 'occupation', n_oc)
    print('unmatched:', unmatched)


if __name__ == '__main__':
    main()
