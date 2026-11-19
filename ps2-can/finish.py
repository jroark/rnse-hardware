import pcbnew as p,pathlib
D=pathlib.Path(__file__).resolve().parent
# Load a clean placement by stripping only top-level routing/zone expressions.
import re
text=(D/'ps2-can.kicad_pcb').read_text()
for match in reversed(list(re.finditer(r'(?m)^\t\((?:segment|via|zone)\b',text))):
 start=match.start();pos=text.index('(',start);depth=0;quoted=False;escape=False
 for j in range(pos,len(text)):
  ch=text[j]
  if escape:escape=False;continue
  if ch=='\\' and quoted:escape=True;continue
  if ch=='"':quoted=not quoted
  if not quoted:
   if ch=='(':depth+=1
   elif ch==')':
    depth-=1
    if depth==0:break
 text=text[:start]+text[j+1:]
clean=D/'reports/placement.kicad_pcb';clean.write_text(text)
b=p.LoadBoard(str(clean))
for net in b.GetNetsByName().values():
 if net.GetNetname().startswith('/'):net.SetNetname(net.GetNetname()[1:])
print('Import',p.ImportSpecctraSES(b,str(D/'final.ses')))
# Remove redundant narrow ground escapes; the two pours carry ground.
# Preserve routed ground tracks for ground-plane connectivity.
# Ground pours on both layers. Signals already routed; refill preserves clearances.
for layer,netname in [(p.F_Cu,'GND'),(p.B_Cu,'GND')]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet(netname));z.SetLocalClearance(p.FromMM(.25));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.35));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
 outline=z.Outline();outline.NewOutline()
 for x,y in [(100.5,100.5),(164.5,100.5),(164.5,144.5),(100.5,144.5)]:outline.Append(int(p.FromMM(x)),int(p.FromMM(y)))
 b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones())
# Use the exact schematic net names, including isolated NC nets.
import xml.etree.ElementTree as ET
expected={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in ET.parse(D/'reports/schematic.xml').findall('.//nets/net') for n in net.findall('node') if not n.attrib['ref'].startswith('#')}
byname=dict(b.GetNetsByName())
for old,net in list(byname.items()):
 old=str(old)
 if old and not old.startswith('unconnected-'):
  net.SetNetname('/'+old.lstrip('/'))
for fp in b.GetFootprints():
 if fp.GetReference().startswith('TP'):
  fp.SetFPID(p.LIB_ID('ps2-can','TestPoint_THTPad_D1.5mm_Drill0.7mm'))
  fp.SetAttributes(fp.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
 for pad in fp.Pads():
  name=expected.get((fp.GetReference(),pad.GetNumber()))
  if name and name.startswith('unconnected-'):
   net=p.NETINFO_ITEM(b,name);b.Add(net);pad.SetNet(net)
# SWIG SaveBoard also writes project defaults; retain explicit project rules.
import json
project=json.loads((D/'ps2-can.kicad_pro').read_text())
project['board']['design_settings']['rules']['min_track_width']=.15
project['net_settings']['classes'][0]['track_width']=.25
p.SaveBoard(str(D/'ps2-can.kicad_pcb'),b)
(D/'ps2-can.kicad_pro').write_text(json.dumps(project,indent=2))
