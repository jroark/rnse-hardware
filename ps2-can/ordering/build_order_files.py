#!/usr/bin/env python3
"""Export distributor upload records from the KiCad BOM; no live cart operations."""
import csv,json,pathlib,collections,urllib.parse
D=pathlib.Path(__file__).resolve().parent.parent
# Distributor identifiers and links transcribed from distributor product listings.
# Quantities and reference groups always come from the design BOM.
catalog={
'1715048':('Phoenix Contact','277-1260-ND','phoenix-contact/1715048/260628'),
'MD-60S':('Same Sky','CP-2460-ND','same-sky-formerly-cui-devices/MD-60S/145311'),
'61300311121':('Wurth Elektronik','732-5316-ND','wurth-electronics/61300311121/4846825'),
'ATTINY1616-SNR':('Microchip Technology','ATTINY1616-SNRCT-ND','microchip-technology/ATTINY1616-SNR/7354620'),
'MCP2515-I/SO':('Microchip Technology','MCP2515-I/SO-ND','microchip-technology/MCP2515-I-SO/593001'),
'TJA1055T/2Z':('NXP Semiconductors','568-TJA1055T/2ZCT-ND','nxp-usa-inc/TJA1055T-2Z/10815724'),
'TSR 1-2450':('TRACO Power','1951-2747-ND','traco-power/TSR-1-2450/9383780'),
'0466.500NR':('Littelfuse','F1454CT-ND','littelfuse-inc/0466-500NR/521335'),
'SS16-E3/61T':('Vishay General Semiconductor','SS16-E3/61TGICT-ND','vishay-general-semiconductor-diodes-division/SS16-E3-61T/1091540'),
'SMBJ18A':('Littelfuse','SMBJ18ALFCT-ND','littelfuse-inc/SMBJ18A/285985'),
'1812L020/60DR':('Littelfuse','F4245CT-ND','littelfuse-inc/1812L020-60DR/3305610'),
'RC0805FR-07100RL':('YAGEO','311-100CRCT-ND','yageo/RC0805FR-07100RL/727543'),
'RC0805FR-074K7L':('YAGEO','311-4.70KCRCT-ND','yageo/RC0805FR-074K7L/727929'),
'RC0805FR-0710KL':('YAGEO','311-10.0KCRCT-ND','yageo/RC0805FR-0710KL/727535'),
'RC0805FR-075K6L':('YAGEO','311-5.60KCRCT-ND','yageo/RC0805FR-075K6L/728002'),
'RC0805FR-071KL':('YAGEO','311-1.00KCRCT-ND','yageo/RC0805FR-071KL/727444'),
'LTST-C170KGKT':('Lite-On','160-1414-1-ND','lite-on-inc/LTST-C170KGKT/386777'),
'LTST-C170KFKT':('Lite-On','160-1413-1-ND','lite-on-inc/LTST-C170KFKT/386775'),
'PESD5V0S1BA,115':('Nexperia','1727-PESD5V0S1BA,115CT-ND','nexperia-usa-inc/PESD5V0S1BA-115/1157463'),
'C0805C104K5RACTU':('KEMET','399-C0805C104K5RACTUCT-ND','kemet/C0805C104K5RACTU/411169'),
'GRM21BR61H106KE43L':('Murata Electronics','490-18663-1-ND','murata-electronics/GRM21BR61H106KE43L/10326316'),
'GRM21BR61C106KE15L':('Murata Electronics','490-3886-1-ND','murata-electronics/GRM21BR61C106KE15L/965900'),
'ABL-16.000MHZ-B2':('Abracon','535-9041-ND','abracon-llc/ABL-16-000MHZ-B2/675236'),
'C0805C270J5GACTU':('KEMET','399-C0805C270J5GACTUCT-ND','kemet/C0805C270J5GACTU/411389')}
notes={
 'MD-60S':'Use date code AFTER 2022-03-03; current footprint. Confirm with supplier.',
 '0466.500NR':'Corrected F1 MPN: 1206 / 500 mA / 63 V. Old 0467.500NRHF was 0603; do not order it.',
 'ABL-16.000MHZ-B2':'Corrected Y1 MPN: through-hole HC-49/US / 16 MHz / 18 pF. ABLS SMD version does not fit.',
 'SS16-E3/61T':'Sourcing replacement for SS16-13-F: Vishay SS16, same SMA / 60 V / 1 A / cathode pad 1.',
 'TJA1055T/2Z':'DigiKey listing shows backorder; Mouser 771-TJA1055T/2Z listing shows stock. Recheck live availability.',
 'PESD5V0S1BA,115':'DigiKey listing shows backorder. Check Mouser stock; use Nexperia listing, not discontinued NXP listing.',
 'GRM21BR61C106KE15L':'DigiKey listing shows backorder. Check Mouser stock or reviewed higher-voltage 0805 equivalent.'}
def natural(ref):return (''.join(c for c in ref if c.isalpha()),int(''.join(c for c in ref if c.isdigit())))
rows=list(csv.DictReader((D/'bom.csv').open(newline='')))
grouped=collections.defaultdict(list)
for row in rows:
 if row['Reference'].startswith('TP'):continue
 assert row['MPN'] in catalog,row
 grouped[row['MPN']].append(row)
master=[];dk=[];mouser=[]
for mpn,group in sorted(grouped.items(),key=lambda pair:min(natural(r['Reference']) for r in pair[1])):
 refs=','.join(sorted((r['Reference'] for r in group),key=natural));qty=len(group)
 manufacturer,sku,path=catalog[mpn]
 url='https://www.digikey.com/en/products/detail/'+path
 master.append([qty,refs,manufacturer,mpn,sku,group[0]['Value'],group[0]['Footprint'],url,'https://www.mouser.com/c/?q='+urllib.parse.quote(mpn,safe=''),notes.get(mpn,'')])
 dk.append([sku,qty,refs])
 mouser.append([mpn,manufacturer,qty,refs])
assert len(master)==24 and sum(row[0] for row in master)==48
flat=[r['Reference'] for group in grouped.values() for r in group]
assert len(flat)==len(set(flat))==48
out=D/'ordering'
def write(name,headers,records):
 with (out/name).open('w',newline='') as f:
  w=csv.writer(f);w.writerow(headers);w.writerows(records)
write('digikey-1-board.csv',['Part Number','Quantity','Customer Reference'],dk)
write('mouser-1-board.csv',['Manufacturer Part Number','Manufacturer','Quantity','Reference Designator'],mouser)
write('bom-ordering-detail.csv',['Quantity','References','Manufacturer','Manufacturer Part Number','DigiKey Part Number','Value','PCB Footprint','DigiKey Product URL','Mouser Search URL','Notes'],master)
# Tab-separated quick-paste data intentionally has no header.
(out/'digikey-quick-paste.txt').write_text(''.join(f'{sku}\t{qty}\n' for sku,qty,refs in dk))
(out/'mouser-quick-paste.txt').write_text(''.join(f'{mpn}\t{qty}\n' for mpn,mfr,qty,refs in mouser))
# Round-trip check: quoted commas, slash-bearing SKUs and all quantities survive export.
for name in ['digikey-1-board.csv','mouser-1-board.csv']:
 parsed=list(csv.DictReader((out/name).open(newline='')))
 assert len(parsed)==24 and sum(int(r['Quantity']) for r in parsed)==48
 assert all(int(r['Quantity'])>0 for r in parsed)
print('Exported two distributor BOMs: 24 order lines, 48 components, one board, no added spares.')
