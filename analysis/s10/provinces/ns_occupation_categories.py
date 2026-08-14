import re
POL=re.compile(r'politician|politican|poltician|poltiician|poliitician|politiican|politcian|school board trustee|member of parliament',re.I)
RULES=[
 ('law',r'lawyer|solicitor|barrister|law professor|legal|notary|q\.c\.'),
 ('health',r'physician|surgeon|nurse|nursing|physiotherap|dentist|chiroprac|paramedic|pharmac|health care|healthcare|psycholog|social worker|counsell|therapist|optometr|veterinar|medical|dietit'),
 ('education',r'teacher|principal|educator|professor|lecturer|instructor|school administrator|school board administrator|guidance|early childhood|preschool|university administrator|librarian|tutor|educational'),
 ('agriculture',r'farmer|farm |agricultur|woodlot|nurseryman|fisher|fish plant|logging|forest|sawyer|orchard|aquacultur|landscap|horticultur'),
 ('communications-PR-journalism',r'journalist|broadcast|reporter|editor|public relations|communications|radio|television|author|writer|publisher|media|camera operator|photographer|interpreter|translator'),
 ('trades-labour',r'electrician|steamfitter|pipefitter|plumber|mechanic|machinist|machine operator|engine operator|plant operator|equipment operator|truck driver|steel worker|welder|carpenter|technician|labour|labor|union|miner|millwright|firefighter|fire chief|police|corrections|safety|maintenance|driver|railway|longshore|steel worker|municipal worker|airline worker|factory worker|construction worker|mill worker|plant worker|station agent|steamship pilot'),
 ('public-service',r'public servant|civil servant|policy analyst|municipal administrator|park planner|cartographer|air force|army|naval|navy|military|soldier|public utility commissioner|executive assistant|administrative assistant|government|deputy minister|diplomat|clerk|public official|economic development officer'),
 ('NGO-advocacy',r'non-?profit|non-?government|ngo|charit|advocacy|community developer|community facilitator|volunteer|foundation|youth organization'),
 ('business',r'business|entrepreneur|merchant|stockbroker|accountant|real estate|insurance|financial|investment|banker|consultant|manager|management|executive|sales|salesman|salesperson|retail|store|restaurant|hotel|contractor|auctioneer|funeral director|surveyor|marketing|proprietor|owner|economist|analyst|realtor|broker|tourism'),
 ('other',r'clergy|priest|minister|deacon|pastor|rabbi|musician|actor|artist|artisitic|potter|ceramic|geologist|architect|engineer|scientist|researcher|pilot|athlete|student|homemaker|chef|cook|designer|programmer|planner|hockey scout|producer|outreach assistant'),
]
PRIORITY=['law','health','education','agriculture','communications-PR-journalism','trades-labour','NGO-advocacy','other','business','public-service']
EXACT={'executive director':'other','director':'other','coordinator':'other'}
def cat1(o):
    if o.strip().lower() in EXACT: return EXACT[o.strip().lower()]
    for c,pat in RULES:
        if re.search(pat,o,re.I): return c
    return None
def category(occs):
    nonpol=[o for o in occs if not POL.search(o)]
    cs=[c for c in (cat1(o) for o in nonpol) if c]
    if cs: return next(p for p in PRIORITY if p in cs)
    if occs: return 'public-service' if any(POL.search(o) for o in occs) else 'unknown'
    return 'unknown'
