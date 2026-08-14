import json,re,sys,collections
sys.path.insert(0,'/tmp/claude-1000/-home-matt-performance-commons/90221613-745b-4ed1-89b6-bc432df3d564/scratchpad')
import cats
PDF='https://nslegislature.ca/sites/default/files/pdfs/people/mlabios.pdf'
entries={r['name']:r for r in json.load(open('ns_entries.json'))}
st=json.load(open('ns_out_stage1.json'))
FILL={
 'Houston, Timothy Jerome':('Chartered Accountant','business','https://web.archive.org/web/20160113031532/http://nslegislature.ca/index.php/people/members/tim_houston'),
 'Dexter, Darrell E.':('Lawyer; Dartmouth City Councillor','law','https://web.archive.org/web/20120130095105/http://nslegislature.ca/index.php/people/members/darrell_dexter'),
 'Martin, Tammy':('Worked at the Nova Scotia Health Authority and the Canadian Union of Public Employees','trades-labour','https://web.archive.org/web/20170609020854/http://nslegislature.ca/index.php/people/members/tammy_martin'),
 'Kousoulis, Labi':('Small business owner','business','https://web.archive.org/web/20140109011744/http://nslegislature.ca/index.php/people/members/labi_kousoulis'),
 'MacKay, Hugh Wilson':('Consultant in the geo-information technologies sector; Executive Director of GeoAlliance Canada','business','https://web.archive.org/web/20170609020849/http://nslegislature.ca/index.php/people/members/hugh_mackay'),
 'Diab, Lena Metlege':('Lawyer and small business owner','law','https://web.archive.org/web/20140109011740/http://nslegislature.ca/index.php/people/members/lena_m_diab'),
 'Smith, Maurice G.':('Lawyer with Nova Scotia Legal Aid; Senior Counsel and managing lawyer','law','https://web.archive.org/web/20120130095157/http://nslegislature.ca/index.php/people/members/maurice_g_smith'),
}
EDU={
 'Adams, Barbara Anne':dict(education_level='bachelor',education_field='physiotherapy',
   alma_maters=['Dalhousie University'],src='https://nslegislature.ca/members/profiles/barbara-adams'),
 'Comer, Brian Keith':dict(education_level='graduate',education_field='health administration; nursing',
   alma_maters=['University of Regina','University of New Brunswick','Cape Breton University'],
   src='https://nslegislature.ca/members/profiles/brian-comer'),
 'MacDonald, Mary Maureen':dict(education_level='graduate',education_field='social work',
   alma_maters=['St. Francis Xavier University','Dalhousie University','University of Warwick'],
   src='https://web.archive.org/web/20120130095126/http://nslegislature.ca/index.php/people/members/maureen_macdonald'),
 'Paris, Percy Alonzo':dict(education_level='bachelor',education_field='arts',
   alma_maters=['Saint Mary’s University'],
   src='https://web.archive.org/web/20120130095145/http://nslegislature.ca/index.php/people/members/percy_paris'),
 'Peterson-Rafuse, Denise':dict(education_level='bachelor',education_field='public relations; broadcasting',
   alma_maters=['Mount Saint Vincent University','Nova Scotia Community College'],
   src='https://web.archive.org/web/20120130095148/http://nslegislature.ca/index.php/people/members/denise_peterson-rafuse'),
}
def clean(o): return re.sub(r'\s{2,}.*$','',o).strip()
recs=[]
for r in st:
    d=r.get('_dirname')
    occs=[clean(o) for o in entries[d]['occ']] if d else []
    rec={'name':r['name'],'education_level':'unknown','education_field':'','alma_maters':[],
         'prior_occupation':'; '.join(occs),'occupation_category':cats.category(occs),
         'source_url':PDF,'directory_entry':d or ''}
    if not occs and d in FILL:
        o,c,u=FILL[d]; rec.update(prior_occupation=o,occupation_category=c,source_url=u)
    if d in EDU:
        e=EDU[d]; rec.update(education_level=e['education_level'],education_field=e['education_field'],
                             alma_maters=e['alma_maters'],education_source_url=e['src'])
    recs.append(rec)
json.dump(recs,open('/home/matt/performance_commons/analysis/s10/provinces/ns_member_bios.json','w'),indent=1)
print('n',len(recs),'occ',sum(1 for r in recs if r['prior_occupation']),'edu',sum(1 for r in recs if r['education_level']!='unknown'))
print(collections.Counter(r['occupation_category'] for r in recs))
