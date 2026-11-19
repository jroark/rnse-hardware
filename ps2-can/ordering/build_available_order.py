#!/usr/bin/env python3
"""Export an order variant based on the user's DigiKey availability export.
Original design BOM is preserved. Run after build_order_files.py.

    python3 build_available_order.py myLists.xlsx
"""
import csv,json,pathlib,collections,hashlib,sys,zipfile,xml.etree.ElementTree as ET
D=pathlib.Path(__file__).resolve().parent
if len(sys.argv)!=2:
 sys.exit('usage: build_available_order.py DIGIKEY_EXPORT.xlsx')
source=pathlib.Path(sys.argv[1])
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(source) as z:
 strings=[''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
 parsed=[]
 for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:sheetData/m:row',ns):
  record={}
  for cell in row.findall('m:c',ns):
   v=cell.find('m:v',ns);value=v.text if v is not None else ''.join(cell.itertext())
   if cell.get('t')=='s':value=strings[int(value)]
   column=''.join(c for c in cell.get('r') if c.isalpha());record[column]=value or ''
  parsed.append(record)
by_mpn={r['B']:r for r in parsed if r.get('B') and r.get('B')!='Manufacturer Part Number'}
unavailable={m for m,r in by_mpn.items() if r.get('F')=='0'}
assert unavailable=={'GRM21BR61H106KE43L','GRM21BR61C106KE15L','PESD5V0S1BA,115','RC0805FR-07100RL','TJA1055T/2Z'}
assert any(r.get('Q')=='Part Number' and not r.get('B') for r in parsed)
audit={'source_file':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'unavailable_lines':[{ 'manufacturer_part_number':m,'quantity':int(by_mpn[m]['I']),'availability':0,'source_row':next(i+1 for i,r in enumerate(parsed) if r is by_mpn[m])} for m in sorted(unavailable)],'invalid_header_import':True}
(D/'availability-export-audit.json').write_text(json.dumps(audit,indent=2))
base=list(csv.DictReader((D/'bom-ordering-detail.csv').open(newline='')))
# These choices retain every PCB footprint. C6 uses the original 50 V C5 part.
replacements={
 'RC0805FR-07100RL':dict(mpn='RC0805FR-07100RP',sku='YAG1318CT-ND',mfr='YAGEO',url='https://www.digikey.com/en/products/detail/yageo/RC0805FR-07100RP/4935333',stock=12150,reason='Same 100 ohm / 1% / 0.125 W / 0805; lead-free RC_P termination variant.'),
 'PESD5V0S1BA,115':dict(mpn='ESD5V0D3B-TP',sku='ESD5V0D3B-TPMSCT-ND',mfr='MCC (Micro Commercial Components)',url='https://www.digikey.com/en/products/detail/mcc-micro-commercial-components/ESD5V0D3B-TP/2213549',stock=57285,reason='5 V bidirectional SOD-323 ESD diode. MCC datasheet: +/-25 kV IEC ESD; 15 V clamp at 8 A; 50 pF max. Functional alternate, not identical surge rating.')}
dk=[];only=[];detail=[];covered=[]
mouser_cap='81-GRM21BR61H106KE3L';mouser_can='771-TJA1055T/2Z'
capurl='https://www.mouser.com/en/ProductDetail/Murata-Electronics/GRM21BR61H106KE43L?qs=lYGu3FyN48cBZlIduWKclg%3D%3D'
canurl='https://www.mouser.com/en/ProductDetail/NXP-Semiconductors/TJA1055T-2Z?qs=qSfuJ%252Bfl%2Fd47IrA1fhktNg%3D%3D'
for r in base:
 mpn=r['Manufacturer Part Number'];qty=int(r['Quantity']);refs=r['References'];covered+=refs.split(',')
 supplier='DigiKey';order_mpn=mpn;sku=r['DigiKey Part Number'];url=r['DigiKey Product URL'];reason='Unchanged; in stock in user-supplied DigiKey export.';stock=by_mpn[mpn]['F']
 if mpn in replacements:
  rep=replacements[mpn];order_mpn=rep['mpn'];sku=rep['sku'];url=rep['url'];reason=rep['reason'];stock=rep['stock'];only.append([sku,qty,refs])
 if refs in ['C5','C6']:
  supplier='Mouser';order_mpn='GRM21BR61H106KE43L';sku=mouser_cap;url=capurl;stock=2639
  reason='Original C5 part; source at Mouser.' if refs=='C5' else '10 uF / X5R / 0805; increase C6 rating from 16 V to 50 V. Same land pattern; no electrical-value or PCB change.'
 elif refs=='U3':
  supplier='Mouser';sku=mouser_can;url=canurl;stock=2263;reason='Keep specified TJA1055T/2Z, source at Mouser. No substitution to /3 or high-speed CAN.'
 else:dk.append([sku,qty,refs])
 detail.append([refs,qty,supplier,mpn,order_mpn,sku,stock,url,reason])
mouser=[[mouser_cap,2,'C5,C6'],[mouser_can,1,'U3']]
def write(name,rows,header=None):
 with (D/name).open('w',newline='') as f:
  w=csv.writer(f)
  if header:w.writerow(header)
  w.writerows(rows)
write('digikey-order-now.csv',dk)
write('mouser-order-now.csv',mouser)
write('digikey-replacements-only.csv',only)
write('availability-replacements.csv',detail,['References','Quantity','Supplier','Design MPN','Order MPN','Supplier Part Number','Stock Shown When Checked','Product URL','Compatibility / Notes'])
assert len(dk)==21 and sum(r[1] for r in dk)==45
assert len(mouser)==2 and sum(r[1] for r in mouser)==3
assert len(covered)==len(set(covered))==48
assert sum(r[1] for r in only)==8
for name,expected in [('digikey-order-now.csv',45),('mouser-order-now.csv',3),('digikey-replacements-only.csv',8)]:
 rows=list(csv.reader((D/name).open(newline='')))
 assert all(len(r)==3 and int(r[1])>0 for r in rows)
 assert sum(int(r[1]) for r in rows)==expected
 assert not any(r[0]=='Part Number' for r in rows)
original={(r['References'],int(r['Quantity'])) for r in base}
actual={(r[0],r[1]) for r in detail}
assert original==actual
print('Verified 48 components: DigiKey 21 lines / 45 pieces; Mouser 2 lines / 3 pieces. Headerless imports checked.')
